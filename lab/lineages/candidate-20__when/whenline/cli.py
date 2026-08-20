from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from .diffio import (
    SourceBag,
    git_diff,
    git_repo_root,
    iter_scan_files,
    parse_colon_target,
    parse_grep_lines,
    parse_unified_diff,
)
from .model import Locus, Query
from .render import render


def _looks_like_diff(text: str) -> bool:
    return (
        text.startswith("diff --git ")
        or text.startswith("--- ")
        or text.startswith("+++ ")
        or "\n@@ " in text[:4000]
        or text.startswith("@@ ")
    )


def _mode(args: argparse.Namespace, n: int, from_diff: bool) -> str:
    if args.json:
        return "json"
    if args.group:
        return "group"
    if args.explain:
        return "explain"
    if args.tsv:
        return "tsv"
    if sys.stdout.isatty() and (n <= 3 or args.explain is True) and not from_diff:
        return "explain"
    if from_diff and sys.stdout.isatty():
        return "group"
    return "tsv"


def _filter(loci: list[Locus], args: argparse.Namespace) -> list[Locus]:
    out = loci
    if args.min_depth:
        out = [loc for loc in out if loc.depth >= args.min_depth]
    if args.errors_only:
        out = [loc for loc in out if loc.error]
    return out


def _scan_paths(paths: list[Path], args: argparse.Namespace) -> list[Locus]:
    loci: list[Locus] = []
    for root in paths:
        for fp in iter_scan_files(root):
            try:
                source = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            from .query import index_source

            idx = index_source(source, str(fp))
            # pick the deepest line per function-ish region: report every line
            # at or above min-depth (default 4 for --scan).
            min_d = args.min_depth if args.min_depth is not None else 4
            best: dict[int, Locus] = {}
            for ln in range(1, idx.nlines + 1):
                loc = idx.at(ln)
                loc.file = str(fp)
                if loc.depth >= min_d and not loc.error:
                    best[ln] = loc
            # compress consecutive lines with the same path_key to the first
            prev_key = None
            for ln in sorted(best):
                loc = best[ln]
                key = loc.path_key
                if key == prev_key:
                    continue
                prev_key = key
                loci.append(loc)
    return loci


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="when",
        description="When does this line run? Path-condition at a source locus.",
        epilog="stdin: unified diff, or rg/grep FILE:LINE output. No args: git diff.",
    )
    p.add_argument("targets", nargs="*", help="FILE:LINE, FILE LINE, FILE, or DIR")
    p.add_argument("--git", action="store_true", help="annotate git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="annotate a unified diff file ('-' = stdin)")
    p.add_argument("--scan", action="store_true", help="walk files, emit deep path-conditions")
    p.add_argument("--min-depth", type=int, default=None, help="keep loci with depth >= N")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="group loci by path-condition")
    p.add_argument("--repo", default=None, help="repo root (default: cwd / git toplevel)")
    p.add_argument("--old", default="HEAD", help="revision for deleted diff lines (default HEAD)")
    p.add_argument("--errors-only", action="store_true")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    return p


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)
    stdin_text = ""
    def _is_tty() -> bool:
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    want_stdin = stdin is not None or args.diff == "-" or (
        not _is_tty() and args.diff in (None, "-")
    )
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin
        stdin_text = src.read()

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    loci: list[Locus] = []
    from_diff = False
    unresolved = 0

    # FILE:LINE / FILE / DIR positional
    queries: list[Query] = []
    scan_roots: list[Path] = []
    i = 0
    targets = list(args.targets)
    while i < len(targets):
        t = targets[i]
        colon = parse_colon_target(t)
        if colon:
            queries.append(colon)
            i += 1
            continue
        p = Path(t)
        # FILE LINE
        if i + 1 < len(targets) and targets[i + 1].isdigit() and (p.exists() or not p.suffix == ""):
            queries.append(Query(file=t, line=int(targets[i + 1])))
            i += 2
            continue
        if p.is_dir() or args.scan:
            scan_roots.append(p)
            i += 1
            continue
        if p.is_file():
            if args.scan:
                scan_roots.append(p)
            elif stdin_text:
                # file is the default path for LINE:text rg output
                pass
            else:
                scan_roots.append(p)
                args.scan = True
                if args.min_depth is None:
                    args.min_depth = 1
            i += 1
            continue
        # maybe FILE:LINE where FILE contains colons (windows) — already handled
        print(f"when: cannot parse target {t!r}", file=sys.stderr)
        return 2

    if args.diff:
        from_diff = True
        if args.diff != "-":
            stdin_text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
        hits = parse_unified_diff(stdin_text)
        for hit in hits:
            loc = bag.resolve_hit(hit, old_rev=args.old)
            if loc.error:
                unresolved += 1
            loci.append(loc)
    elif args.git or (not targets and not stdin_text and not args.scan):
        from_diff = True
        if git_repo_root(repo) is None:
            print("when: not a git repository", file=sys.stderr)
            return 3
        text = git_diff(repo, [])
        hits = parse_unified_diff(text)
        for hit in hits:
            loc = bag.resolve_hit(hit, old_rev=args.old)
            if loc.error:
                unresolved += 1
            loci.append(loc)
    elif stdin_text:
        if _looks_like_diff(stdin_text):
            from_diff = True
            for hit in parse_unified_diff(stdin_text):
                loc = bag.resolve_hit(hit, old_rev=args.old)
                if loc.error:
                    unresolved += 1
                loci.append(loc)
        else:
            default_file = None
            file_targets = [t for t in targets if Path(t).is_file() and not parse_colon_target(t)]
            if len(file_targets) == 1:
                default_file = file_targets[0]
            for q in parse_grep_lines(stdin_text, default_file=default_file):
                loc = bag.resolve_query(q)
                if loc.error:
                    unresolved += 1
                loci.append(loc)
            if not loci and stdin_text.strip():
                print(
                    "when: stdin is not a diff or file:line stream "
                    "(for rg FILE, pass the file: rg -n PAT FILE | when FILE)",
                    file=sys.stderr,
                )
                return 2

    for q in queries:
        loc = bag.resolve_query(q)
        if loc.error:
            unresolved += 1
        loci.append(loc)

    if scan_roots or (args.scan and not loci):
        roots = scan_roots or [Path.cwd()]
        loci.extend(_scan_paths(roots, args))

    loci = _filter(loci, args)

    if args.quiet:
        return 1 if unresolved else 0

    mode = _mode(args, len(loci), from_diff)
    text = render(loci, mode=mode)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    if not loci:
        return 1 if unresolved else 0
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
