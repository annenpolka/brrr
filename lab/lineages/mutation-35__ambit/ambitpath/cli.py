from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterator, Optional, TextIO

from .diffio import (
    PrefixedStream,
    git_diff,
    git_repo_root,
    parse_colon_target,
    parse_grep_lines,
    parse_locator_line,
    parse_unified_diff,
    recover_file_from_pins,
    SourceBag,
)
from .match import Matcher, split_snippets
from .query import query_file
from .render import render, write_chunk
from .scan import filter_loci, matcher_from_locus, scan_file, scan_paths


def _looks_like_diff(text: str) -> bool:
    return (
        text.startswith("diff --git ")
        or text.startswith("--- ")
        or text.startswith("+++ ")
        or "\n@@ " in text[:4000]
        or text.startswith("@@ ")
    )


def _mode(args: argparse.Namespace, *, from_stream: bool, n: Optional[int] = None) -> str:
    if args.json:
        return "json"
    if args.group:
        return "group"
    if args.explain:
        return "explain"
    if args.tsv:
        return "tsv"
    if from_stream:
        return "tsv"
    if sys.stdout.isatty() and n is not None and n <= 6:
        return "explain"
    return "tsv"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ambit",
        description=(
            "The ambit of a predicate: name a snippet, emit every locus whose "
            "path-condition contains it. Files come from stdin locators "
            "(rg | ambit) or FILE operands — not a tree walk."
        ),
        epilog="Mutation of under(1): default scan is the file stdin named.",
    )
    p.add_argument(
        "predicate",
        nargs="?",
        help="predicate / condition snippet (or 'A | B' for AND)",
    )
    p.add_argument(
        "paths",
        nargs="*",
        help="FILE to scan (DIR only with --walk). Default: files named on stdin",
    )
    p.add_argument("--and", dest="also", action="append", default=[], help="AND another snippet")
    p.add_argument(
        "--kind",
        action="append",
        default=[],
        help="only match this frame kind (given, if, guard, …); repeatable",
    )
    p.add_argument("--regex", action="store_true", help="treat snippets as regex")
    p.add_argument(
        "--eval",
        dest="include_eval",
        action="store_true",
        help="also match eval frames (the if-line itself)",
    )
    p.add_argument(
        "--fn",
        dest="include_struct",
        action="store_true",
        help="also match fn/class/impl frames",
    )
    p.add_argument("--all", action="store_true", help="every matching line, no span collapse")
    p.add_argument(
        "--same-as",
        metavar="FILE:LINE",
        help="use that locus's in-force conditions as the snippet (AND)",
    )
    p.add_argument(
        "--hits",
        action="store_true",
        help="keep only stdin locator lines (filter), do not scan their files",
    )
    p.add_argument(
        "--walk",
        action="store_true",
        help="scan DIR operands (and cwd if none); off by default",
    )
    p.add_argument("--git", action="store_true", help="filter git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="filter a unified diff file ('-' = stdin)")
    p.add_argument("--min-depth", type=int, default=None, help="keep loci with depth >= N")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster by matched predicate (buffers)")
    p.add_argument("--repo", default=None, help="repo root (default: cwd / git toplevel)")
    p.add_argument("--old", default="HEAD", help="revision for deleted diff lines")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    return p


def _build_matcher(args: argparse.Namespace) -> tuple[Matcher, list[Path]]:
    snippets: list[str] = []
    paths = [Path(p) for p in args.paths]
    if args.predicate:
        pred_path = Path(args.predicate)
        if pred_path.exists():
            paths = [pred_path, *paths]
        else:
            snippets.extend(split_snippets(args.predicate))
    for extra in args.also:
        snippets.extend(split_snippets(extra))
    expanded: list[str] = []
    for s in snippets:
        expanded.extend(split_snippets(s))
    snippets = expanded

    if args.same_as:
        q = parse_colon_target(args.same_as)
        if q is None:
            raise SystemExit(f"ambit: --same-as expects FILE:LINE, got {args.same_as!r}")
        loc = query_file(q.file, q.line)
        if loc.error:
            raise SystemExit(f"ambit: --same-as {args.same_as}: {loc.error}")
        derived = matcher_from_locus(loc)
        snippets = list(derived.snippets) + snippets

    kinds = set(args.kind) if args.kind else None
    return (
        Matcher(
            snippets=snippets,
            kinds=kinds,
            regex=args.regex,
            include_eval=args.include_eval,
            include_struct=args.include_struct,
        ),
        paths,
    )


def _want_stdin(args: argparse.Namespace, stdin: Optional[TextIO]) -> bool:
    if stdin is not None:
        return True
    if args.diff == "-":
        return True
    try:
        return not sys.stdin.isatty()
    except Exception:
        return False


def _emit(
    hits: list,
    args: argparse.Namespace,
    *,
    from_stream: bool,
    mode: Optional[str] = None,
    already: int = 0,
    buffered: Optional[list] = None,
) -> tuple[int, str]:
    if args.min_depth is not None:
        hits = [h for h in hits if h.loc.depth >= args.min_depth]
    if buffered is not None:
        buffered.extend(hits)
        return already, mode or "group"
    if args.quiet:
        return already + len(hits), "quiet"
    if mode is None:
        mode = _mode(args, from_stream=from_stream, n=len(hits) if not from_stream else None)
    if mode == "group":
        if buffered is None:
            return already, mode
        return already, mode
    n = write_chunk(sys.stdout, hits, mode=mode, already=already)
    return n, mode


def _scan_named_files(
    files: Iterator[Path],
    matcher: Matcher,
    args: argparse.Namespace,
    *,
    from_stream: bool,
) -> int:
    collapse = not args.all
    already = 0
    mode: Optional[str] = None
    buffered: Optional[list] = [] if (args.group and not args.quiet) else None
    any_file = False
    for fp in files:
        any_file = True
        hits = scan_file(fp, matcher, collapse=collapse)
        already, mode = _emit(
            hits,
            args,
            from_stream=from_stream,
            mode=mode,
            already=already,
            buffered=buffered,
        )
        if args.quiet:
            already = already  # counted inside _emit
    if not any_file:
        return 1
    if args.quiet:
        return 0 if already else 1
    if buffered is not None:
        if args.min_depth is not None:
            buffered = [h for h in buffered if h.loc.depth >= args.min_depth]
        text = render(buffered, mode="group")
        if text:
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
        return 0 if buffered else 1
    return 0 if already else 1


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        matcher, paths = _build_matcher(args)
    except SystemExit:
        raise
    if not matcher.snippets and not args.same_as:
        print("ambit: name a predicate snippet (or --same-as FILE:LINE)", file=sys.stderr)
        return 2

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    collapse = not args.all
    file_targets = [p for p in paths if p.is_file()]
    dir_targets = [p for p in paths if p.is_dir()]
    default_file = str(file_targets[0]) if len(file_targets) == 1 else None

    want_stdin = _want_stdin(args, stdin)
    src: Optional[TextIO] = None
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin

    try:
        return _dispatch(
            args,
            matcher,
            paths,
            file_targets,
            dir_targets,
            default_file,
            bag,
            collapse,
            src,
        )
    except BrokenPipeError:
        return 0


def _dispatch(
    args: argparse.Namespace,
    matcher: Matcher,
    paths: list[Path],
    file_targets: list[Path],
    dir_targets: list[Path],
    default_file: Optional[str],
    bag: SourceBag,
    collapse: bool,
    src: Optional[TextIO],
) -> int:
    prefixed: Optional[PrefixedStream] = None
    if src is not None:
        prefixed = PrefixedStream(src)
        if args.diff or args.git or _looks_like_diff(prefixed.head):
            return _run_diff(args, matcher, bag, collapse, prefixed)
        return _run_stream(
            args, matcher, file_targets, dir_targets, default_file, collapse, prefixed, bag
        )

    return _run_args_only(args, matcher, paths, file_targets, dir_targets)


def _run_diff(
    args: argparse.Namespace,
    matcher: Matcher,
    bag: SourceBag,
    collapse: bool,
    prefixed: PrefixedStream,
) -> int:
    if args.diff and args.diff != "-":
        text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
    elif args.git:
        repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
        if git_repo_root(repo) is None:
            print("ambit: not a git repository", file=sys.stderr)
            return 3
        text = git_diff(repo, [])
    else:
        text = prefixed.remainder_text()
    loci = [bag.resolve_hit(hit, old_rev=args.old) for hit in parse_unified_diff(text)]
    hits = filter_loci(loci, matcher, collapse=collapse)
    return _finish_batch(hits, args, from_stream=True)


def _unique_files(locators, file_targets: list[Path], repo: Optional[Path]) -> list[Path]:
    """Files stdin named. Bare LINE:text recovers a unique git-listed file."""
    files: list[Path] = []
    seen: set[str] = set()
    bare = []
    for loc in locators:
        if loc.file:
            key = loc.file
            if key not in seen:
                seen.add(key)
                files.append(Path(loc.file))
        elif loc.line is not None:
            bare.append(loc)
    if files:
        return files
    if not bare:
        return []
    recovered = recover_file_from_pins(bare, extra_files=file_targets, repo=repo)
    return [recovered] if recovered is not None else []


def _run_stream(
    args: argparse.Namespace,
    matcher: Matcher,
    file_targets: list[Path],
    dir_targets: list[Path],
    default_file: Optional[str],
    collapse: bool,
    prefixed: PrefixedStream,
    bag: SourceBag,
) -> int:
    # Locator text is small (rg hits). Scan/output still streams per file.
    lines = list(prefixed.lines())
    locators = [parse_locator_line(raw, default_file=default_file) for raw in lines]
    locators = [p for p in locators if p is not None]
    nonempty = any(raw.strip() for raw in lines)
    if not locators:
        if nonempty:
            print(
                "ambit: stdin is not a diff or file:line stream "
                "(pass FILE after the predicate, or rg -nH / rg -l)",
                file=sys.stderr,
            )
            return 2
        return _run_args_only(args, matcher, file_targets + dir_targets, file_targets, dir_targets)

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or None)
    files = _unique_files(locators, file_targets, repo)

    if args.hits:
        bound = default_file or (str(files[0]) if len(files) == 1 else None)
        queries = parse_grep_lines("".join(lines), default_file=bound)
        queries = [q for q in queries if q.file]
        if not queries:
            print(
                "ambit: --hits needs line locators (rg -n), not a file list",
                file=sys.stderr,
            )
            return 2
        loci = [bag.resolve_query(q) for q in queries]
        hits = filter_loci(loci, matcher, collapse=collapse)
        return _finish_batch(hits, args, from_stream=True)

    if not files:
        print(
            "ambit: LINE:text locators need a FILE operand, rg -nH, or a unique "
            "match in this git tree (cd to the repo rg searched)",
            file=sys.stderr,
        )
        return 2

    def gen() -> Iterator[Path]:
        yield from files

    return _scan_named_files(gen(), matcher, args, from_stream=True)


def _run_args_only(
    args: argparse.Namespace,
    matcher: Matcher,
    paths: list[Path],
    file_targets: list[Path],
    dir_targets: list[Path],
) -> int:
    if dir_targets and not args.walk:
        shown = dir_targets[0]
        print(
            f"ambit: will not walk {shown} (pipe rg locators, pass FILE, or --walk)",
            file=sys.stderr,
        )
        return 2
    if file_targets and not args.walk:
        return _scan_named_files(iter(file_targets), matcher, args, from_stream=False)
    if args.walk:
        roots = paths or [Path.cwd()]
        hits = scan_paths(roots, matcher, collapse=not args.all)
        return _finish_batch(hits, args, from_stream=False)
    print(
        "ambit: name files on argv or pipe locators (rg -nH / rg -l). No cwd walk.",
        file=sys.stderr,
    )
    return 2


def _finish_batch(hits: list, args: argparse.Namespace, *, from_stream: bool) -> int:
    if args.min_depth is not None:
        hits = [h for h in hits if h.loc.depth >= args.min_depth]
    if args.quiet:
        return 0 if hits else 1
    mode = _mode(args, from_stream=from_stream, n=len(hits))
    text = render(hits, mode=mode)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
