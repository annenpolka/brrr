"""neap CLI — exclusive-A deaths of an unapplied overlay. Never writes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence, TextIO

from .overlay import looks_like_diff, overlay_diff
from .stacks import NeapReport, neap_from_images


class NeapError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="neap",
        description=(
            "Overlay a unified diff in memory onto --base and emit the "
            "exclusive-A path-condition stacks that would die. Not the "
            "stacks the patch births. Never writes the worktree. Does not "
            "walk cwd."
        ),
        epilog=(
            "stdin is a unified diff. Default leftover stays on deleted "
            "files; --also-changed names vanished stacks inside surviving "
            "files. A move is silent. Exit 0 deaths, 1 none, 2 usage."
        ),
    )
    p.add_argument("-C", "--repo", default=None, help="repo root (git -C). Default: cwd")
    p.add_argument(
        "--base",
        default="HEAD",
        help="pre-image revision to overlay onto (default HEAD). :wt = worktree",
    )
    p.add_argument("--diff", metavar="PATCH", help="unified diff file ('-' = stdin)")
    p.add_argument("--json", action="store_true", help="JSON report")
    p.add_argument("--tsv", action="store_true", help="TSV: side role label file line")
    p.add_argument("--oneline", action="store_true", help="one stack per line")
    p.add_argument(
        "--limit",
        type=int,
        default=8,
        help="max exclusive-A (dead) stacks to name (default: 8)",
    )
    p.add_argument(
        "--also-changed",
        action="store_true",
        help="also name exclusive-A stacks that died inside surviving files",
    )
    p.add_argument(
        "--grain",
        choices=("files", "functions", "loci"),
        default="files",
    )
    p.add_argument("--with-fn", action="store_true", help="include fn frames in stack identity")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    p.add_argument("--selftest", action="store_true")
    p.add_argument(
        "targets",
        nargs="*",
        help="optional path filters (not a tree walk)",
    )
    return p


def _read_diff(args: argparse.Namespace, stdin: TextIO) -> str:
    if args.diff in (None, "-"):
        if args.diff is None and stdin.isatty():
            raise NeapError(
                "usage: neap --diff PATCH | neap < patch  (stdin is a unified diff)",
                2,
            )
        text = stdin.read()
    else:
        path = Path(args.diff)
        if path.is_dir():
            raise NeapError(f"refusing to walk directory: {path}", 2)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise NeapError(f"cannot read {path}: {exc}", 2) from exc
    if not text.strip():
        raise NeapError("empty diff", 2)
    if not looks_like_diff(text):
        raise NeapError("stdin/file is not a unified diff", 2)
    return text


def _repo(args: argparse.Namespace) -> Path:
    root = Path(args.repo).resolve() if args.repo else Path.cwd()
    if not root.is_dir():
        raise NeapError(f"not a directory: {root}", 2)
    return root


def _refuse_walk(targets: Sequence[str], root: Path) -> Optional[set]:
    if not targets:
        return None
    wanted: set[str] = set()
    for t in targets:
        p = Path(t)
        if p.is_dir() or (not p.is_absolute() and (root / t).is_dir()):
            raise NeapError(f"refusing to walk directory: {t}", 2)
        wanted.add(t)
    return wanted


def format_human(report: NeapReport, *, repo: Path, base: str) -> str:
    name = repo.name or str(repo)
    d = report.delta
    lines = [
        f"# neap overlay onto {base}  ({name})",
        f"# A  {base}  (pre-image, never written)",
        "# B  overlay (in memory)",
    ]
    bits = []
    if d.only_a:
        bits.append(f"{len(d.only_a)} only-A")
    if d.only_b:
        bits.append(f"{len(d.only_b)} only-B")
    if d.changed:
        bits.append(f"{len(d.changed)} changed")
    if d.renamed:
        bits.append(f"{len(d.renamed)} renamed")
    if d.unplaced:
        bits.append(f"{len(d.unplaced)} unplaced")
    lines.append("# " + ", ".join(bits) if bits else "# empty overlay")
    lines.append("")
    lines.append("neap  (exclusive-A path-conditions that would die)")
    if report.covering:
        for s in report.covering:
            lines.append(f"  A   exclusive_a  {s.label}")
            n = len(s.paths_a)
            files = f"{n} file" + ("" if n == 1 else "s")
            lines.append(f"           {files}  depth={s.depth}")
            if s.holders_a:
                lines.append("           holders A: " + ", ".join(s.holders_a[:6]))
            pin = s.pin_for_true()
            if pin:
                lines.append(f"           pin  {pin[0]}:{pin[1]}")
    else:
        lines.append("  (empty — nothing died)")
    if d.unplaced:
        lines.append("")
        lines.append("unplaced  " + ", ".join(d.unplaced[:6]))
    lines.append(
        f"neap={len(report.covering)}  deaths={report.death_n}  "
        f"born={report.born_n}  moves={report.move_n}"
    )
    return "\n".join(lines)


def format_tsv(report: NeapReport) -> str:
    rows = []
    for s in report.covering:
        pin = s.pin_for_true()
        path = pin[0] if pin else (s.paths_a[0] if s.paths_a else "")
        line = pin[1] if pin else 0
        rows.append("\t".join(["A", s.role, s.label, path, str(line)]))
    return "\n".join(rows)


def format_oneline(report: NeapReport) -> str:
    return "\n".join(f"A\t{s.label}" for s in report.covering)


def format_json(report: NeapReport, *, repo: Path, base: str) -> str:
    d = report.delta
    return json.dumps(
        {
            "repo": str(repo),
            "base": base,
            "identical": not (d.only_a or d.only_b or d.changed or d.renamed),
            "delta": {
                "deleted": len(d.only_a),
                "added": len(d.only_b),
                "changed": len(d.changed),
                "renamed": len(d.renamed),
                "only_a": d.only_a,
                "only_b": d.only_b,
                "changed_paths": d.changed,
            },
            "neap": [s.to_record() for s in report.covering],
            "deaths": report.death_n,
            "born": report.born_n,
            "moves": report.move_n,
            "unplaced": d.unplaced,
        },
        indent=2,
        ensure_ascii=False,
    )


def selftest() -> int:
    from .overlay import PatchFile, apply_hunks, parse_unified_diff
    from .stacks import Stack, cond_label, dead_cover, stacks_in_source

    fails = 0

    def check(name: str, cond: bool) -> None:
        nonlocal fails
        if cond:
            print(f"  ok  {name}")
        else:
            fails += 1
            print(f"  FAIL  {name}", file=sys.stderr)

    src = (
        "def process(ready=True, x=1):\n"
        "    if not ready:\n"
        "        return None\n"
        "    if x > 0:\n"
        "        return 'ok'\n"
    )
    hits = stacks_in_source(src, "src/app.py", grain="files")
    keys = list(hits)
    check("discovered a path-condition", bool(keys))
    labels = [ " | ".join(f"{k} {p}".strip() for k, p in key) for key in keys ]
    check(
        "ready given + x>0 is a stack",
        any("ready" in lab and "x > 0" in lab.replace(" ", "") or "x>0" in lab.replace(" ", "") for lab in labels)
        or any("x > 0" in lab or "x>0" in lab.replace(" ", "") for lab in labels),
    )

    river = Stack(
        key=(("if", "flow_score > 0.2"),),
        holders_a=["src/river.py"],
        holders_b=[],
        paths_a=["src/river.py"],
        paths_b=[],
        pin_a=("src/river.py", 2),
        pin_b=None,
    )
    flood = []
    for i in range(8):
        p = f"src/mod{i}.py"
        s = Stack(
            key=(("if", f"unique_mod_{i} > 0"),),
            holders_a=[],
            holders_b=[p],
            paths_a=[],
            paths_b=[p],
            pin_a=None,
            pin_b=(p, 2),
        )
        flood.append(s)
    move = Stack(
        key=(("given", "ready"), ("if", "x > 0")),
        holders_a=["src/git.py"],
        holders_b=["src/parse.py"],
        paths_a=["src/git.py"],
        paths_b=["src/parse.py"],
        pin_a=("src/git.py", 4),
        pin_b=("src/parse.py", 4),
    )
    tick = Stack(
        key=(("if", "idle<thresholds.t1"),),
        holders_a=["src/core.py"],
        holders_b=[],
        paths_a=["src/core.py"],
        paths_b=[],
        pin_a=("src/core.py", 40),
        pin_b=None,
    )
    check("move is not exclusive-A", move.true_on == "AB" and move.role == "move")
    check("flood members are exclusive-B", all(s.true_on == "B" for s in flood))
    dead = dead_cover([river, *flood, move, tick], ["src/river.py"], limit=4)
    check("dead cover keeps the island", any(s.key == river.key for s in dead))
    check("dead cover ignores exclusive-B flood", all(s.true_on == "A" for s in dead))
    check("dead cover ignores the move", all(s.role != "move" for s in dead))
    check("default leftover ignores surviving-file exclusive-A", all(s.key != tick.key for s in dead))
    dead2 = dead_cover([river, tick], ["src/river.py"], limit=6, also_changed=True)
    check("--also-changed includes surviving-file exclusive-A", any(s.key == tick.key for s in dead2))

    # Overlay apply never needs a worktree write.
    diff = (
        "diff --git a/src/river.py b/src/river.py\n"
        "deleted file mode 100644\n"
        "--- a/src/river.py\n"
        "+++ /dev/null\n"
        "@@ -1,3 +0,0 @@\n"
        "-def bar_color(flow_score):\n"
        "-    if flow_score > 0.2:\n"
        "-        return 'flow'\n"
    )
    files = parse_unified_diff(diff)
    check("parsed a delete", len(files) == 1 and files[0].is_delete)
    post, added, err = apply_hunks(
        "def bar_color(flow_score):\n    if flow_score > 0.2:\n        return 'flow'\n",
        files[0],
    )
    check("delete overlay post is empty", not (post or "").strip() and err is None)
    check("delete overlay has no added lines", added == [])

    swift = (
        "struct Row {\n"
        "    var barColor: Int {\n"
        "        if app.flowScore > 0.2 {\n"
        "            return 1\n"
        "        }\n"
        "        return 0\n"
        "    }\n"
        "    var stored = 1\n"
        "}\n"
    )
    shits = stacks_in_source(swift, "row.swift")
    check(
        "computed var if is a stack",
        any("flowScore" in cond_label(k) for k in shits),
    )
    check("stored var is not a stack", not any("stored" in cond_label(k) for k in shits))

    if fails:
        print(f"selftest FAIL={fails}", file=sys.stderr)
        return 1
    print("selftest ok")
    return 0


def run(argv: Optional[Sequence[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else sys.argv[1:])
    if args.selftest:
        return selftest()
    stdin = stdin if stdin is not None else sys.stdin
    try:
        text = _read_diff(args, stdin)
        root = _repo(args)
        wanted = _refuse_walk(args.targets, root)
        images = overlay_diff(text, root, base=args.base, path_filter=wanted)
        if not images:
            raise NeapError("diff named no files", 2)
        report = neap_from_images(
            images,
            grain=args.grain,
            with_fn=bool(args.with_fn),
            limit=args.limit,
            also_changed=bool(args.also_changed),
        )
        if not args.quiet:
            if args.json:
                print(format_json(report, repo=root, base=args.base))
            elif args.tsv:
                text_out = format_tsv(report)
                if text_out:
                    print(text_out)
            elif args.oneline:
                text_out = format_oneline(report)
                if text_out:
                    print(text_out)
            else:
                print(format_human(report, repo=root, base=args.base))
        unplaced_only = bool(report.delta.unplaced) and not (
            report.delta.only_a or report.delta.only_b or report.delta.changed or report.delta.renamed
        )
        if unplaced_only:
            return 2
        return 0 if report.covering else 1
    except NeapError as exc:
        print(f"neap: {exc}", file=sys.stderr)
        return exc.code


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        return run(argv)
    except KeyboardInterrupt:
        print("neap: interrupted", file=sys.stderr)
        return 130
