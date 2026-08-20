from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from .diffio import (
    git_diff,
    git_repo_root,
    parse_colon_target,
    parse_grep_lines,
    parse_unified_diff,
    SourceBag,
)
from .match import Matcher, split_snippets
from .query import query_file
from .render import render
from .scan import filter_loci, matcher_from_locus, scan_paths


def _looks_like_diff(text: str) -> bool:
    return (
        text.startswith("diff --git ")
        or text.startswith("--- ")
        or text.startswith("+++ ")
        or "\n@@ " in text[:4000]
        or text.startswith("@@ ")
    )


def _mode(args: argparse.Namespace, n: int, from_stream: bool) -> str:
    if args.json:
        return "json"
    if args.group:
        return "group"
    if args.explain:
        return "explain"
    if args.tsv:
        return "tsv"
    if sys.stdout.isatty() and n <= 6 and not from_stream:
        return "explain"
    if from_stream and sys.stdout.isatty():
        return "group"
    return "tsv"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="under",
        description=(
            "Where does this condition hold? "
            "Name a predicate snippet; emit every locus whose path-condition contains it."
        ),
        epilog="Reverse of when(1): when names a line, under names a condition.",
    )
    p.add_argument(
        "predicate",
        nargs="?",
        help="predicate / condition snippet (or 'A | B' for AND)",
    )
    p.add_argument("paths", nargs="*", help="FILE or DIR to scan (default: cwd)")
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
    p.add_argument("--git", action="store_true", help="filter git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="filter a unified diff file ('-' = stdin)")
    p.add_argument("--min-depth", type=int, default=None, help="keep loci with depth >= N")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster by matched predicate")
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
            raise SystemExit(f"under: --same-as expects FILE:LINE, got {args.same_as!r}")
        loc = query_file(q.file, q.line)
        if loc.error:
            raise SystemExit(f"under: --same-as {args.same_as}: {loc.error}")
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


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)

    def _is_tty() -> bool:
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    stdin_text = ""
    want_stdin = stdin is not None or args.diff == "-" or (
        not _is_tty() and args.diff in (None, "-")
    )
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin
        stdin_text = src.read()

    try:
        matcher, paths = _build_matcher(args)
    except SystemExit:
        raise
    if not matcher.snippets and not args.same_as:
        print("under: name a predicate snippet (or --same-as FILE:LINE)", file=sys.stderr)
        return 2

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    collapse = not args.all
    hits = []
    from_stream = False

    if args.diff or args.git or (stdin_text and _looks_like_diff(stdin_text)):
        from_stream = True
        if args.diff and args.diff != "-":
            text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
        elif args.git:
            if git_repo_root(repo) is None:
                print("under: not a git repository", file=sys.stderr)
                return 3
            text = git_diff(repo, [])
        else:
            text = stdin_text
        loci = [bag.resolve_hit(hit, old_rev=args.old) for hit in parse_unified_diff(text)]
        hits = filter_loci(loci, matcher, collapse=collapse)
    elif stdin_text and not _looks_like_diff(stdin_text):
        from_stream = True
        default_file = None
        file_targets = [p for p in paths if p.is_file()]
        if len(file_targets) == 1:
            default_file = str(file_targets[0])
        queries = parse_grep_lines(stdin_text, default_file=default_file)
        if not queries and stdin_text.strip():
            print(
                "under: stdin is not a diff or file:line stream "
                "(pass FILE after the predicate for rg FILE)",
                file=sys.stderr,
            )
            return 2
        loci = [bag.resolve_query(q) for q in queries]
        hits = filter_loci(loci, matcher, collapse=collapse)
    else:
        roots = paths or [Path.cwd()]
        hits = scan_paths(roots, matcher, collapse=collapse)

    if args.min_depth is not None:
        hits = [h for h in hits if h.loc.depth >= args.min_depth]

    if args.quiet:
        return 0 if hits else 1

    mode = _mode(args, len(hits), from_stream)
    text = render(hits, mode=mode)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
