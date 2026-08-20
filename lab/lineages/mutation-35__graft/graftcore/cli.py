from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, TextIO

from .index import query_file, query_source
from .model import Locus
from .overlay import is_git_repo, looks_like_diff, overlay_diff, read_worktree
from .render import render


def _mode(args: argparse.Namespace, n: int) -> str:
    if args.json:
        return "json"
    if args.group:
        return "group"
    if args.explain:
        return "explain"
    if args.tsv:
        return "tsv"
    if sys.stdout.isatty() and n <= 8:
        return "explain"
    return "tsv"


def _parse_colon(spec: str) -> Optional[tuple[str, int]]:
    if ":" not in spec:
        return None
    file, _, rest = spec.rpartition(":")
    if not file or not rest.isdigit():
        # FILE:LINE:col
        parts = spec.rsplit(":", 2)
        if len(parts) == 3 and parts[1].isdigit():
            return parts[0], int(parts[1])
        if len(parts) >= 2 and parts[-1].isdigit():
            return ":".join(parts[:-1]), int(parts[-1])
        return None
    return file, int(rest)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graft",
        description=(
            "Path-condition stack on the post-image of an unapplied patch. "
            "Reads a unified diff, overlays it in memory (never writes the "
            "worktree), and prints when each added line would run."
        ),
        epilog=(
            "Default: stdin or --diff is a unified diff; each '+' line is "
            "answered on the post-image. HEAD-only lookup is --now FILE:LINE. "
            "Exit 0 if every added line is placed, 1 if a locus cannot be "
            "placed, 2 on usage/error."
        ),
    )
    p.add_argument(
        "-C",
        "--repo",
        default=None,
        help="repo root (git -C). Default: cwd",
    )
    p.add_argument(
        "--base",
        default="HEAD",
        help="pre-image revision to overlay onto (default HEAD). Use :wt for worktree",
    )
    p.add_argument(
        "--diff",
        metavar="PATCH",
        help="unified diff file ('-' = stdin)",
    )
    p.add_argument(
        "--now",
        action="store_true",
        help="opt-in HEAD/worktree lookup (no overlay). Requires FILE:LINE",
    )
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="group added lines by path-condition")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    p.add_argument(
        "targets",
        nargs="*",
        help="with --diff: path filters. with --now: FILE:LINE",
    )
    return p


def _unplaced(loc: Locus) -> bool:
    return (not loc.placed) or bool(loc.error)


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)

    def _is_tty() -> bool:
        try:
            return sys.stdin.isatty()
        except Exception:
            return False

    stdin_text = ""
    want_stdin = stdin is not None or args.diff == "-" or (
        not _is_tty() and args.diff is None and not args.now
    )
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin
        stdin_text = src.read()

    root = Path(args.repo).resolve() if args.repo else Path.cwd()
    if args.repo and not root.is_dir():
        print(f"graft: -C {args.repo} is not a directory", file=sys.stderr)
        return 2

    loci: list[Locus] = []

    if args.now:
        if args.diff:
            print("graft: --now is HEAD-only; drop --diff or drop --now", file=sys.stderr)
            return 2
        specs: list[tuple[str, int]] = []
        i = 0
        targets = list(args.targets)
        while i < len(targets):
            t = targets[i]
            colon = _parse_colon(t)
            if colon:
                specs.append(colon)
                i += 1
                continue
            if i + 1 < len(targets) and targets[i + 1].isdigit():
                specs.append((t, int(targets[i + 1])))
                i += 2
                continue
            print(f"graft: --now needs FILE:LINE, got {t!r}", file=sys.stderr)
            return 2
        if not specs:
            print("graft: --now requires FILE:LINE (HEAD-only is opt-in)", file=sys.stderr)
            return 2
        for file, line in specs:
            source = None
            if is_git_repo(root) and args.base not in {":wt", ".", "WORKTREE", "worktree"}:
                from .overlay import git_show

                rel = file
                rp = Path(file)
                try:
                    rel = str(rp.resolve().relative_to(root))
                except Exception:
                    rel = file
                source = git_show(root, args.base, rel)
            if source is None:
                source = read_worktree(root, file)
            if source is None:
                p = Path(file)
                if p.is_file():
                    try:
                        source = p.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        source = None
            if source is None:
                loc = Locus(
                    file=file,
                    line=line,
                    here="",
                    engine="none",
                    error="source unavailable",
                    side=".",
                    image="now",
                    placed=False,
                )
            else:
                loc = query_source(source, file, line)
                loc.side = "."
                loc.image = "now"
                if loc.error:
                    loc.placed = False
            loci.append(loc)
    else:
        diff_text = stdin_text
        if args.diff and args.diff != "-":
            p = Path(args.diff)
            if not p.is_file():
                print(f"graft: --diff {args.diff} not found", file=sys.stderr)
                return 2
            diff_text = p.read_text(encoding="utf-8", errors="replace")
        if not diff_text.strip():
            print(
                "graft: pass a unified diff on stdin or --diff FILE "
                "(HEAD-only is --now FILE:LINE)",
                file=sys.stderr,
            )
            return 2
        if not looks_like_diff(diff_text):
            print("graft: stdin/--diff is not a unified diff", file=sys.stderr)
            return 2
        path_filter = set(args.targets) if args.targets else None
        images = overlay_diff(diff_text, root=root, base=args.base, path_filter=path_filter)
        if not images:
            print("graft: no file hunks in diff", file=sys.stderr)
            return 1
        for img in images:
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
                loc = query_source(img.post, ad.path, ad.line)
                loc.side = "+"
                loc.image = "post"
                if not loc.here:
                    loc.here = ad.text
                if loc.error:
                    loc.placed = False
                loci.append(loc)

    unplaced = sum(1 for loc in loci if _unplaced(loc))

    if args.quiet:
        return 1 if unplaced else 0

    mode = _mode(args, len(loci))
    text = render(loci, mode=mode)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    if not loci:
        return 1
    return 1 if unplaced else 0


if __name__ == "__main__":
    raise SystemExit(main())
