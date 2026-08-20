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
from .query import query_file
from .render import render
from .scan import filter_loci, scan_paths


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
    if sys.stdout.isatty() and n <= 8 and not from_stream:
        return "explain"
    if from_stream and sys.stdout.isatty():
        return "group"
    return "tsv"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chime",
        description=(
            "Control-flow rhyme: name a locus; emit other loci whose "
            "path-condition is the same stack, or a superset (deeper nest)."
        ),
        epilog=(
            "Flip of when(1): when prints the stack at a line. "
            "chime names the line and finds the other lines that share it. "
            "Not under(1): under matches a predicate snippet."
        ),
    )
    p.add_argument(
        "target",
        nargs="?",
        help="FILE:LINE seed (or use --same-as)",
    )
    p.add_argument("paths", nargs="*", help="FILE or DIR to scan (default: the seed's file)")
    p.add_argument(
        "--same-as",
        metavar="FILE:LINE",
        help="seed locus (alias of the FILE:LINE operand)",
    )
    p.add_argument(
        "--exact",
        action="store_true",
        help="only identical stacks; drop deeper (superset) nests",
    )
    p.add_argument(
        "--any-fn",
        action="store_true",
        help="rhyme across functions (default: same function as the seed)",
    )
    p.add_argument(
        "--eval",
        dest="include_eval",
        action="store_true",
        help="include eval frames in the stack key (the if-line itself)",
    )
    p.add_argument("--all", action="store_true", help="every matching line, no span collapse")
    p.add_argument(
        "--braces",
        action="store_true",
        help="keep blank / `{` / `}` lines (default: drop them as span noise)",
    )
    p.add_argument(
        "--others",
        action="store_true",
        help="omit the seed line from the hits",
    )
    p.add_argument("--git", action="store_true", help="filter git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="filter a unified diff file ('-' = stdin)")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster by same vs deeper")
    p.add_argument("--repo", default=None, help="repo root (default: cwd / git toplevel)")
    p.add_argument("--old", default="HEAD", help="revision for deleted diff lines")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    return p


def _seed_from_args(args: argparse.Namespace) -> tuple[str, int]:
    spec = args.same_as or args.target
    if not spec:
        raise SystemExit("chime: name a locus (FILE:LINE or --same-as FILE:LINE)")
    q = parse_colon_target(spec)
    if q is None:
        # FILE LINE was not used; maybe they passed a bare path as target
        # and --same-as is missing.
        raise SystemExit(f"chime: expected FILE:LINE, got {spec!r}")
    return q.file, q.line


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
        seed_file, seed_line = _seed_from_args(args)
    except SystemExit as e:
        if e.code and isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise

    seed = query_file(seed_file, seed_line)
    if seed.error:
        print(f"chime: {seed_file}:{seed_line}: {seed.error}", file=sys.stderr)
        return 1
    if not seed.cond_key(include_eval=args.include_eval):
        print(
            f"chime: {seed_file}:{seed_line}: no path-condition "
            "(top-level / function preamble)",
            file=sys.stderr,
        )
        return 1

    paths = [Path(p) for p in args.paths]
    # If the positional target was FILE:LINE, remaining args are scan roots.
    # If --same-as was used, args.target may be a scan path.
    if args.same_as and args.target:
        tpath = Path(args.target)
        if tpath.exists() and parse_colon_target(args.target) is None:
            paths = [tpath, *paths]

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    collapse = not args.all
    from_stream = False
    hits = []

    kw = dict(
        exact=args.exact,
        include_eval=args.include_eval,
        any_fn=args.any_fn,
        collapse=collapse,
        payload=True,
        braces=args.braces,
    )

    if args.diff or args.git or (stdin_text and _looks_like_diff(stdin_text)):
        from_stream = True
        if args.diff and args.diff != "-":
            text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
        elif args.git:
            if git_repo_root(repo) is None:
                print("chime: not a git repository", file=sys.stderr)
                return 3
            text = git_diff(repo, [])
        else:
            text = stdin_text
        loci = [bag.resolve_hit(hit, old_rev=args.old) for hit in parse_unified_diff(text)]
        hits = filter_loci(loci, seed, **kw)
    elif stdin_text and not _looks_like_diff(stdin_text):
        from_stream = True
        default_file = seed_file
        file_targets = [p for p in paths if p.is_file()]
        if len(file_targets) == 1:
            default_file = str(file_targets[0])
        queries = parse_grep_lines(stdin_text, default_file=default_file)
        if not queries and stdin_text.strip():
            print(
                "chime: stdin is not a diff or file:line stream "
                "(rg -n PAT FILE | chime FILE:LINE)",
                file=sys.stderr,
            )
            return 2
        loci = [bag.resolve_query(q) for q in queries]
        hits = filter_loci(loci, seed, **kw)
    else:
        roots = paths or [Path(seed_file)]
        hits = scan_paths(roots, seed, **kw)

    if args.others:
        hits = [h for h in hits if not h.seed]

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
