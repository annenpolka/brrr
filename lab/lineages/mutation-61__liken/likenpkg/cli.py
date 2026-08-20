from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, TextIO

from .index import query_source
from .model import Locus, is_payload
from .overlay import looks_like_diff, overlay_diff
from .query import (
    Clause,
    looks_like_pin,
    parse_colon,
    parse_path_query,
    path_matches,
    stack_matches,
    under_seed,
)
from .render import render


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="liken",
        description=(
            "Invert of graft: overlay a unified diff in memory and emit the "
            "added lines that share a path-condition stack. Never writes the "
            "worktree. Does not walk cwd."
        ),
        epilog=(
            "stdin is a unified diff. --same-as is a post-image FILE:LINE or a "
            "stack path like 'fn parse_header | given starts_with(a/)'. "
            "Without --same-as, group every added line by stack. "
            "Exit 0 found, 1 none, 2 usage."
        ),
    )
    p.add_argument("-C", "--repo", default=None, help="repo root (git -C). Default: cwd")
    p.add_argument(
        "--base",
        default="HEAD",
        help="pre-image revision to overlay onto (default HEAD). :wt = worktree",
    )
    p.add_argument("--diff", metavar="PATCH", help="unified diff file ('-' = stdin)")
    p.add_argument(
        "--same-as",
        dest="same_as",
        metavar="QUERY",
        help="FILE:LINE (post-image) or 'kind pred | …' stack path",
    )
    p.add_argument("--kind", default=None, help="restrict snippet clauses to this frame kind")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster hits by exact stack")
    p.add_argument(
        "--payload",
        action="store_true",
        help="drop brace/comment husks (default on explain/group)",
    )
    p.add_argument(
        "--husks",
        action="store_true",
        help="keep brace/comment husks in explain/group",
    )
    p.add_argument(
        "--exact",
        action="store_true",
        help="FILE:LINE matches only the identical stack (default for pins)",
    )
    p.add_argument(
        "--under",
        action="store_true",
        help="FILE:LINE matches any superstack (deeper ifs ride along)",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    p.add_argument(
        "targets",
        nargs="*",
        help="optional path filters (not a tree walk)",
    )
    return p


def _mode(args: argparse.Namespace) -> str:
    if args.json:
        return "json"
    if args.tsv:
        return "tsv"
    if args.group and not args.same_as:
        return "group"
    if args.group and args.same_as:
        return "group"
    if args.explain:
        return "explain"
    if args.same_as:
        return "explain"
    return "group"


def _loci_from_images(images, path_filter) -> List[Locus]:
    loci: List[Locus] = []
    for img in images:
        if path_filter and not any(path_matches(img.path, f) for f in path_filter):
            continue
        if img.binary:
            loci.append(
                Locus(
                    file=img.path,
                    line=0,
                    here="",
                    engine="none",
                    error=img.error or "binary patch",
                    side="+",
                    image="post",
                    placed=False,
                )
            )
            continue
        if img.error and not img.added:
            loci.append(
                Locus(
                    file=img.path,
                    line=0,
                    here="",
                    engine="none",
                    error=img.error,
                    side="+",
                    image="post",
                    placed=False,
                )
            )
            continue
        if img.post is None:
            for ad in img.added:
                loci.append(
                    Locus(
                        file=ad.path,
                        line=ad.line,
                        here=ad.text,
                        engine="none",
                        error=ad.error or img.error or "unplaced",
                        side="+",
                        image="post",
                        placed=False,
                    )
                )
            continue
        idx_source = img.post
        for ad in img.added:
            if ad.error:
                loci.append(
                    Locus(
                        file=ad.path,
                        line=ad.line,
                        here=ad.text,
                        engine="none",
                        error=ad.error,
                        side="+",
                        image="post",
                        placed=False,
                    )
                )
                continue
            loc = query_source(idx_source, ad.path, ad.line)
            loc.side = "+"
            loc.image = "post"
            if not loc.here:
                loc.here = ad.text
            if loc.error:
                loc.placed = False
            loci.append(loc)
    return loci


def _filter_same_as(
    loci: List[Locus],
    images,
    query: str,
    kind: Optional[str],
    *,
    pin_exact: bool = True,
) -> List[Locus]:
    placed = [loc for loc in loci if loc.placed and not loc.error]
    if looks_like_pin(query):
        pin = parse_colon(query)
        if pin is None:
            return []
        file, line = pin
        seed: Optional[Locus] = None
        for loc in placed:
            if path_matches(loc.file, file) and loc.line == line:
                seed = loc
                break
        if seed is None:
            # locus may be context, not a + line — look it up on the post-image
            for img in images:
                if img.post is None:
                    continue
                if not path_matches(img.path, file):
                    continue
                seed = query_source(img.post, img.path, line)
                seed.side = "."
                seed.image = "post"
                break
        if seed is None or seed.error:
            return []
        seed_frames = seed.cond_frames
        hits = []
        for loc in placed:
            if not path_matches(loc.file, file):
                continue
            if pin_exact:
                if loc.path_key == seed.path_key:
                    hits.append(loc)
            elif under_seed(seed_frames, loc.cond_frames):
                hits.append(loc)
        return hits

    clauses = parse_path_query(query)
    if kind:
        clauses = [
            Clause(kind=kind, pred=c.pred, inverted=c.inverted) if c.kind is None else c
            for c in clauses
        ]
        if len(clauses) == 1 and clauses[0].kind is None:
            clauses = [Clause(kind=kind, pred=clauses[0].pred, inverted=clauses[0].inverted)]
        elif clauses and all(c.kind is None for c in clauses):
            clauses = [Clause(kind=kind, pred=c.pred, inverted=c.inverted) for c in clauses]
        elif clauses:
            # apply --kind only to clauses that didn't name one
            clauses = [
                Clause(kind=c.kind or kind, pred=c.pred, inverted=c.inverted) for c in clauses
            ]
    return [loc for loc in placed if stack_matches(loc.cond_frames, clauses)]


def main(argv: Optional[List[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)

    def _is_tty() -> bool:
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    stdin_text = ""
    want_stdin = stdin is not None or args.diff == "-" or (
        not _is_tty() and args.diff is None
    )
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin
        stdin_text = src.read()

    root = Path(args.repo).resolve() if args.repo else Path.cwd()
    if args.repo and not root.is_dir():
        print("liken: -C {} is not a directory".format(args.repo), file=sys.stderr)
        return 2

    # refuse a cwd walk: a directory operand is usage, not a scan
    for t in args.targets:
        p = Path(t)
        if p.is_dir():
            print(
                "liken: {} is a directory; will not walk cwd. Pipe a unified diff.".format(t),
                file=sys.stderr,
            )
            return 2

    diff_text = stdin_text
    if args.diff and args.diff != "-":
        p = Path(args.diff)
        if not p.is_file():
            print("liken: --diff {} not found".format(args.diff), file=sys.stderr)
            return 2
        diff_text = p.read_text(encoding="utf-8", errors="replace")
    if not diff_text.strip():
        print(
            "liken: pass a unified diff on stdin or --diff FILE "
            "(the locus is the post-image; this is not a HEAD walker)",
            file=sys.stderr,
        )
        return 2
    if not looks_like_diff(diff_text):
        print("liken: stdin/--diff is not a unified diff", file=sys.stderr)
        return 2

    path_filter = set(args.targets) if args.targets else None
    images = overlay_diff(diff_text, root=root, base=args.base, path_filter=path_filter)
    if not images:
        print("liken: no file hunks in diff", file=sys.stderr)
        return 1

    loci = _loci_from_images(images, path_filter)
    query = args.same_as
    pin_exact = not args.under
    if args.exact:
        pin_exact = True
    if query:
        hits = _filter_same_as(loci, images, query, args.kind, pin_exact=pin_exact)
    else:
        hits = [loc for loc in loci if loc.placed and not loc.error]

    mode = _mode(args)
    payload = False
    if mode in {"explain", "group"}:
        payload = not args.husks
    if args.payload:
        payload = True
        hits = [loc for loc in hits if is_payload(loc.here)]

    if args.quiet:
        return 0 if hits else 1

    text = render(hits, mode=mode, query=query, payload=payload)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
