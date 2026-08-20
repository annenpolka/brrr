from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .brace_eng import query_braces, scan_braces
from .diffio import (
    DiffHit,
    GrepHit,
    looks_like_diff,
    looks_like_grep,
    parse_grep_lines,
    parse_unified_diff,
    walk_sources,
)
from .model import Locus, engine_for
from .python_eng import query_python, scan_python
from .render import render_explain, render_group, render_json, render_tsv


def main(argv: list[str] | None = None, stdin=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    stdin = sys.stdin if stdin is None else stdin
    args = _parse(argv)

    try:
        loci = collect(args, stdin)
    except UsageError as exc:
        print(f"whence: {exc}", file=sys.stderr)
        return 2
    except NotGit as exc:
        print(f"whence: {exc}", file=sys.stderr)
        return 3

    if args.min_depth is not None:
        loci = [loc for loc in loci if loc.error or loc.depth >= args.min_depth]
    if args.errors_only:
        loci = [loc for loc in loci if loc.error]

    if not args.quiet:
        _emit(args, loci)
    if any(loc.error for loc in loci):
        return 1
    return 0


class UsageError(Exception):
    pass


class NotGit(Exception):
    pass


def _parse(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="whence",
        description="When does this line run? Path-condition at a source locus.",
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
    return p.parse_args(argv)


def collect(args: argparse.Namespace, stdin) -> list[Locus]:
    repo = _repo(args)
    targets = _pair_targets(args.targets)

    stdin_text = ""
    if not stdin.isatty():
        stdin_text = stdin.read()

    if args.diff is not None:
        text = stdin_text if args.diff == "-" else Path(args.diff).read_text(encoding="utf-8", errors="replace")
        return _from_diff(text, repo, args.old)

    if args.git:
        return _from_git(repo, args.old)

    if stdin_text:
        if looks_like_diff(stdin_text):
            return _from_diff(stdin_text, repo, args.old)
        default_file = None
        file_targets = [t for t in targets if t[1] is None]
        if len(file_targets) == 1 and Path(file_targets[0][0]).is_file():
            default_file = file_targets[0][0]
        if looks_like_grep(stdin_text, default_file):
            hits = parse_grep_lines(stdin_text, default_file)
            if not hits:
                raise UsageError(
                    "stdin is not a diff or file:line stream "
                    "(for rg FILE, pass the file: rg -n PAT FILE | whence FILE)"
                )
            return [_query_hit(h.file, h.line, repo) for h in hits]
        if not targets:
            raise UsageError(
                "stdin is not a diff or file:line stream "
                "(for rg FILE, pass the file: rg -n PAT FILE | whence FILE)"
            )

    if not targets and not args.scan:
        return _from_git(repo, args.old)

    loci: list[Locus] = []
    walk_roots: list[Path] = []
    for file, line in targets:
        path = _resolve(file, repo)
        if line is not None:
            loci.append(query_path(path, line, file_display=file))
        else:
            walk_roots.append(path)
    if args.scan and not walk_roots and not targets:
        walk_roots.append(repo)
    if args.scan or walk_roots:
        min_d = args.min_depth
        if min_d is None and (args.scan or any(p.is_dir() for p in walk_roots)):
            min_d = 4
        for root in walk_roots:
            for src in walk_sources(root):
                rel = str(src)
                scanned = scan_path(src, display=_display_path(src, repo, file))
                if min_d is not None:
                    scanned = [loc for loc in scanned if loc.depth >= min_d]
                loci.extend(scanned)
    return loci


def _pair_targets(raw: list[str]) -> list[tuple[str, int | None]]:
    out: list[tuple[str, int | None]] = []
    i = 0
    while i < len(raw):
        tok = raw[i]
        if i + 1 < len(raw) and _is_int(raw[i + 1]) and ":" not in tok:
            n = int(raw[i + 1])
            if n < 0:
                raise UsageError(f"cannot parse target '{tok}:{raw[i+1]}'")
            out.append((tok, n))
            i += 2
            continue
        if ":" in tok:
            file, _, rhs = tok.rpartition(":")
            if _is_int(rhs):
                n = int(rhs)
                if n < 0:
                    raise UsageError(f"cannot parse target '{tok}'")
                if not file:
                    raise UsageError(f"cannot parse target '{tok}'")
                out.append((file, n))
                i += 1
                continue
        out.append((tok, None))
        i += 1
    return out


def _is_int(s: str) -> bool:
    if s.startswith("-"):
        return s[1:].isdigit()
    return s.isdigit()


def _repo(args: argparse.Namespace) -> Path:
    if args.repo:
        return Path(args.repo).expanduser().resolve()
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(top)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def _resolve(file: str, repo: Path) -> Path:
    p = Path(file)
    if p.exists():
        return p
    cand = repo / file
    if cand.exists():
        return cand
    return p


def _display_path(src: Path, repo: Path, original: str) -> str:
    try:
        return str(src.relative_to(Path.cwd()))
    except ValueError:
        return str(src)


def query_path(path: Path, line: int, file_display: str | None = None) -> Locus:
    display = file_display if file_display is not None else str(path)
    if not path.is_file():
        loc = Locus(file=display, line=line, engine="none", error="source unavailable")
        return loc.finalize()
    source = path.read_text(encoding="utf-8", errors="replace")
    eng = engine_for(path)
    if eng == "python-ast":
        loc = query_python(display, source, line)
    else:
        loc = query_braces(display, source, line)
    loc.file = display
    return loc


def scan_path(path: Path, display: str | None = None) -> list[Locus]:
    display = display or str(path)
    if not path.is_file():
        return []
    source = path.read_text(encoding="utf-8", errors="replace")
    eng = engine_for(path)
    if eng == "python-ast":
        loci = scan_python(display, source)
    else:
        loci = scan_braces(display, source, events_only=True)
    for loc in loci:
        loc.file = display
    return loci


def _query_hit(file: str, line: int, repo: Path) -> Locus:
    path = _resolve(file, repo)
    loc = query_path(path, line, file_display=file)
    return loc


def _from_diff(text: str, repo: Path, old: str) -> list[Locus]:
    hits = parse_unified_diff(text)
    loci: list[Locus] = []
    for h in hits:
        if h.side == "-":
            loc = _query_old(h, repo, old)
        else:
            path = _resolve(h.path, repo)
            loc = query_path(path, h.line, file_display=h.path)
        loc.side = h.side
        loci.append(loc)
    return loci


def _query_old(h: DiffHit, repo: Path, old: str) -> Locus:
    try:
        blob = subprocess.check_output(
            ["git", "-C", str(repo), "show", f"{old}:{h.path}"],
            stderr=subprocess.DEVNULL,
        )
        source = blob.decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        path = _resolve(h.path, repo)
        if path.is_file():
            return query_path(path, h.line, file_display=h.path)
        loc = Locus(file=h.path, line=h.line, engine="none", error="source unavailable", side="-")
        return loc.finalize()
    eng = engine_for(h.path)
    if eng == "python-ast":
        loc = query_python(h.path, source, h.line)
    else:
        loc = query_braces(h.path, source, h.line)
    return loc


def _from_git(repo: Path, old: str) -> list[Locus]:
    try:
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise NotGit("not a git repository") from exc
    if probe.returncode != 0:
        raise NotGit("not a git repository")
    text = subprocess.check_output(
        ["git", "-C", str(repo), "diff", "--no-ext-diff", "-U0"],
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if not text.strip():
        return []
    return _from_diff(text, repo, old)


def _emit(args: argparse.Namespace, loci: list[Locus]) -> None:
    if args.json:
        for loc in loci:
            print(render_json(loc))
        return
    if args.explain:
        print("\n".join(render_explain(loc) for loc in loci))
        return
    if args.group:
        text = render_group(loci)
        if text:
            print(text)
        return
    if args.tsv:
        for loc in loci:
            print(render_tsv(loc))
        return
    # default: explain on a tty for a few loci, else tsv
    if sys.stdout.isatty() and 0 < len(loci) <= 4:
        print("\n".join(render_explain(loc) for loc in loci))
        return
    for loc in loci:
        print(render_tsv(loc))
