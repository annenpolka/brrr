from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Iterator, Optional, TextIO

from .diffio import (
    SourceBag,
    git_diff,
    git_repo_root,
    parse_colon_target,
    parse_unified_diff,
)
from .derive import derive_snippets
from .locators import StreamNote, files_from_diff, iter_queries, looks_like_diff
from .match import Matcher, split_snippets
from .query import query_file
from .render import render, render_hit
from .scan import Hit, filter_loci, matcher_from_locus, scan_one_file, scan_paths


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
    if sys.stdout.isatty() and (n is None or n <= 6):
        return "explain"
    return "tsv"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amid",
        description=(
            "Where does this condition hold, in the same file as these locators? "
            "Pipe rg/grep hits; emit every locus in those files whose path-condition "
            "contains the named predicate. A stream, not a tree walk."
        ),
        epilog=(
            "Flip of under(1): under walks a tree. "
            "amid scans the files the locators already named (rg | amid PRED)."
        ),
    )
    p.add_argument(
        "predicate",
        nargs="?",
        help="predicate / condition snippet (or 'A | B' for AND)",
    )
    p.add_argument(
        "paths",
        nargs="*",
        help="FILE for bare LINE:text locators, or files to scan when stdin is empty",
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
        "--pin",
        action="store_true",
        help="keep only the piped locators (filter), do not scan their files",
    )
    p.add_argument(
        "--tree",
        action="store_true",
        help="allow walking a named directory (refused by default)",
    )
    p.add_argument("--git", action="store_true", help="take files from git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="take files from a unified diff ('-' = stdin)")
    p.add_argument("--min-depth", type=int, default=None, help="keep loci with depth >= N")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster by matched predicate")
    p.add_argument("--repo", default=None, help="repo root (default: cwd / git toplevel)")
    p.add_argument("--old", default="HEAD", help="revision for deleted diff lines (--pin)")
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
            raise SystemExit(f"amid: --same-as expects FILE:LINE, got {args.same_as!r}")
        loc = query_file(q.file, q.line)
        if loc.error:
            raise SystemExit(f"amid: --same-as {args.same_as}: {loc.error}")
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


def _default_file(paths: list[Path]) -> Optional[str]:
    files = [p for p in paths if p.is_file()]
    if len(files) == 1:
        return str(files[0])
    return None


def _resolve_path(spec: str, repo: Path) -> Path:
    p = Path(spec)
    if p.exists():
        return p
    alt = repo / spec
    if alt.exists():
        return alt
    return p


def _emit(hits: Iterable[Hit], *, mode: str, quiet: bool, min_depth: Optional[int]) -> int:
    n = 0
    first = True
    buf: list[Hit] = []
    collect = mode == "group"
    for h in hits:
        if min_depth is not None and h.loc.depth < min_depth:
            continue
        n += 1
        if quiet:
            continue
        if collect:
            buf.append(h)
            continue
        text = render_hit(h, mode=mode)
        if not text:
            continue
        if mode == "explain" and not first:
            sys.stdout.write("\n")
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
        first = False
    if collect and not quiet:
        text = render(buf, mode="group")
        if text:
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
    return n


def _scan_named(paths: list[Path], matcher: Matcher, *, tree: bool, collapse: bool) -> Iterator[Hit]:
    for p in paths:
        if p.is_file():
            yield from scan_one_file(p, matcher, collapse=collapse)
            continue
        if p.is_dir():
            if not tree:
                raise SystemExit(
                    f"amid: refusing to walk {p} (pipe locators, pass a FILE, or --tree)"
                )
            yield from scan_paths([p], matcher, collapse=collapse)
            continue
        raise SystemExit(f"amid: not a file: {p}")


def _iter_file_hits(
    files: Iterable[str],
    matcher: Matcher,
    *,
    repo: Path,
    collapse: bool,
    seen: Optional[set[str]] = None,
) -> Iterator[Hit]:
    if seen is None:
        seen = set()
    for spec in files:
        path = _resolve_path(spec, repo)
        key = str(path.resolve()) if path.exists() else spec
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            continue
        yield from scan_one_file(path, matcher, collapse=collapse)


def _peek_lines(stream: TextIO, n: int = 24) -> tuple[list[str], bool]:
    buf: list[str] = []
    for _ in range(n):
        line = stream.readline()
        if line == "":
            return buf, True
        buf.append(line)
    return buf, False


def _stdin_kind(head: str) -> str:
    if looks_like_diff(head):
        return "diff"
    return "locators"


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)

    def _is_tty() -> bool:
        try:
            src = stdin if stdin is not None else sys.stdin
            return src.isatty()
        except Exception:
            return False

    try:
        matcher, paths = _build_matcher(args)
    except SystemExit:
        raise
    need_derive = not matcher.snippets and not args.same_as

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    collapse = not args.all

    src = stdin if stdin is not None else sys.stdin
    take_stdin = (
        stdin is not None
        or args.diff == "-"
        or args.git
        or (args.diff is None and not _is_tty())
    )

    # --- git / named patch file ---
    if args.git:
        if git_repo_root(repo) is None:
            print("amid: not a git repository", file=sys.stderr)
            return 3
        text = git_diff(repo, [])
        return _run_diff_text(
            text, args, matcher, bag, repo, collapse, need_derive=need_derive
        )
    if args.diff and args.diff != "-":
        text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
        return _run_diff_text(
            text, args, matcher, bag, repo, collapse, need_derive=need_derive
        )

    if take_stdin:
        head_lines, eof = _peek_lines(src, 24)
        head = "".join(head_lines)
        if not head.strip() and eof:
            # empty stdin: fall through to named files
            pass
        elif _stdin_kind(head) == "diff":
            rest = src.read() if not eof else ""
            return _run_diff_text(
                head + rest, args, matcher, bag, repo, collapse, need_derive=need_derive
            )
        else:
            def line_stream() -> Iterator[str]:
                yield from head_lines
                if not eof:
                    yield from src

            default_file = _default_file(paths)
            note = StreamNote()
            queries = iter_queries(
                line_stream(), default_file=default_file, note=note
            )
            return _run_locator_stream(
                queries,
                args,
                matcher,
                bag,
                repo,
                collapse,
                head,
                note=note,
                need_derive=need_derive,
            )

    # No stdin payload. Explicit files only — never cwd.
    if need_derive:
        print(
            "amid: name a predicate, or pipe locators that point at one "
            "(rg --json 'starts_with' FILE | amid)",
            file=sys.stderr,
        )
        return 2
    if not paths:
        print(
            "amid: pipe locators (rg -nH … | amid PRED) or name a FILE",
            file=sys.stderr,
        )
        return 2

    try:
        hits = list(_scan_named(paths, matcher, tree=args.tree, collapse=collapse))
    except SystemExit as e:
        msg = str(e)
        if msg:
            print(msg, file=sys.stderr)
        return 2

    mode = _mode(args, from_stream=False, n=len(hits))
    n = _emit(hits, mode=mode, quiet=args.quiet, min_depth=args.min_depth)
    return 0 if n else 1


def _run_diff_text(
    text: str,
    args: argparse.Namespace,
    matcher: Matcher,
    bag: SourceBag,
    repo: Path,
    collapse: bool,
    *,
    need_derive: bool = False,
) -> int:
    mode = _mode(args, from_stream=True)
    if need_derive:
        from .model import Query

        queries = [
            Query(file=hit.path, line=hit.line, side=hit.side, here=hit.text)
            for hit in parse_unified_diff(text)
        ]
        n = _emit(
            _iter_derived_hits(queries, args, bag, repo, collapse),
            mode=mode,
            quiet=args.quiet,
            min_depth=args.min_depth,
        )
        return 0 if n else 1
    if args.pin:
        loci = [bag.resolve_hit(hit, old_rev=args.old) for hit in parse_unified_diff(text)]
        hits = filter_loci(loci, matcher, collapse=collapse)
        n = _emit(hits, mode=mode, quiet=args.quiet, min_depth=args.min_depth)
        return 0 if n else 1
    n = _emit(
        _iter_file_hits(files_from_diff(text), matcher, repo=repo, collapse=collapse),
        mode=mode,
        quiet=args.quiet,
        min_depth=args.min_depth,
    )
    return 0 if n else 1


def _run_locator_stream(
    queries: Iterable,
    args: argparse.Namespace,
    matcher: Matcher,
    bag: SourceBag,
    repo: Path,
    collapse: bool,
    head: str,
    *,
    note: StreamNote,
    need_derive: bool,
) -> int:
    mode = _mode(args, from_stream=True)
    saw = False

    def watched() -> Iterator:
        nonlocal saw
        for q in queries:
            saw = True
            yield q

    if need_derive:
        n = _emit(
            _iter_derived_hits(
                watched(),
                args,
                bag,
                repo,
                collapse,
            ),
            mode=mode,
            quiet=args.quiet,
            min_depth=args.min_depth,
        )
        if not saw:
            return _no_locators(head, note)
        return 0 if n else 1

    if args.pin:
        n = _emit(
            _pin_stream(watched(), matcher, bag, collapse),
            mode=mode,
            quiet=args.quiet,
            min_depth=args.min_depth,
        )
        if not saw:
            return _no_locators(head, note)
        return 0 if n else 1

    n = _emit(
        _iter_file_hits(
            (q.file for q in watched()),
            matcher,
            repo=repo,
            collapse=collapse,
        ),
        mode=mode,
        quiet=args.quiet,
        min_depth=args.min_depth,
    )
    if not saw:
        return _no_locators(head, note)
    return 0 if n else 1


def _no_locators(head: str, note: StreamNote) -> int:
    if note.bare_no_file:
        print(
            "amid: locators are LINE:text with no file "
            "(rg FILE omits the name). Pass the FILE, or use rg -nH / rg --json.",
            file=sys.stderr,
        )
        return 2
    if head.strip():
        print(
            "amid: stdin is not a locator stream "
            "(rg -nH FILE, rg --json FILE, or LINE:text plus a FILE operand)",
            file=sys.stderr,
        )
        return 2
    print(
        "amid: pipe locators (rg -nH … | amid PRED) or name a FILE",
        file=sys.stderr,
    )
    return 2


def _iter_derived_hits(
    queries: Iterable,
    args: argparse.Namespace,
    bag: SourceBag,
    repo: Path,
    collapse: bool,
) -> Iterator[Hit]:
    """Each locator names a condition; scan its file for that condition."""
    seen: set[tuple[str, str]] = set()
    emitted: set[tuple[str, int, int]] = set()
    kinds = set(args.kind) if args.kind else None
    for q in queries:
        loc = bag.resolve_query(q)
        if loc.error:
            continue
        snippets = derive_snippets(loc, peel_intro=not args.pin)
        path = _resolve_path(q.file, repo)
        key_file = str(path.resolve()) if path.exists() else q.file
        for snip in snippets:
            pair = (key_file, snip)
            if pair in seen:
                continue
            seen.add(pair)
            derived = Matcher(
                snippets=[snip],
                kinds=kinds,
                regex=args.regex,
                include_eval=args.include_eval,
                include_struct=args.include_struct,
            )
            if args.pin:
                yield from filter_loci([loc], derived, collapse=collapse)
                continue
            if not path.is_file():
                continue
            for h in scan_one_file(path, derived, collapse=collapse):
                ek = (h.loc.file, h.start, h.end)
                if ek in emitted:
                    continue
                emitted.add(ek)
                yield h


def _pin_stream(queries: Iterable, matcher: Matcher, bag: SourceBag, collapse: bool) -> Iterator[Hit]:
    if collapse:
        # collapse needs adjacency; buffer per file
        from collections import defaultdict

        by_file: dict[str, list] = defaultdict(list)
        order: list[str] = []
        for q in queries:
            if q.file not in by_file:
                order.append(q.file)
            by_file[q.file].append(q)
        for path in order:
            loci = [bag.resolve_query(q) for q in by_file[path]]
            yield from filter_loci(loci, matcher, collapse=True)
        return
    for q in queries:
        loc = bag.resolve_query(q)
        yield from filter_loci([loc], matcher, collapse=False)


if __name__ == "__main__":
    sys.exit(main())
