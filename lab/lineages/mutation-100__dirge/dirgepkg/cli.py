"""dirge CLI — clustered exclusive-A deaths of an unapplied overlay. Never writes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence, TextIO

from .overlay import looks_like_diff, overlay_diff
from .stacks import DirgeReport, dirge_from_images


class DirgeError(Exception):
    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dirge",
        description=(
            "Overlay a unified diff in memory onto --base and emit the "
            "exclusive-A path-conditions that would die, clustered as one "
            "obituary per sibling-arm fork (if / elif / given-else / "
            "sequential if). Not the stacks the patch births. Never writes "
            "the worktree. Does not walk cwd."
        ),
        epilog=(
            "stdin is a unified diff. Default leftover stays on deleted "
            "files; --also-changed names vanished stacks inside surviving "
            "files. A move is silent. Sibling arms occupy one covering slot. "
            "Exit 0 deaths, 1 none, 2 usage."
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
    p.add_argument("--tsv", action="store_true", help="TSV: side role label file line arms")
    p.add_argument("--oneline", action="store_true", help="one obituary per line")
    p.add_argument(
        "--limit",
        type=int,
        default=8,
        help="max obituaries (clustered exclusive-A forks) to name (default: 8)",
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
            raise DirgeError(
                "usage: dirge --diff PATCH | dirge < patch  (stdin is a unified diff)",
                2,
            )
        text = stdin.read()
    else:
        path = Path(args.diff)
        if path.is_dir():
            raise DirgeError(f"refusing to walk directory: {path}", 2)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise DirgeError(f"cannot read {path}: {exc}", 2) from exc
    if not text.strip():
        raise DirgeError("empty diff", 2)
    if not looks_like_diff(text):
        raise DirgeError("stdin/file is not a unified diff", 2)
    return text


def _repo(args: argparse.Namespace) -> Path:
    root = Path(args.repo).resolve() if args.repo else Path.cwd()
    if not root.is_dir():
        raise DirgeError(f"not a directory: {root}", 2)
    return root


def _refuse_walk(targets: Sequence[str], root: Path) -> Optional[set]:
    if not targets:
        return None
    wanted: set[str] = set()
    for t in targets:
        p = Path(t)
        if p.is_dir() or (not p.is_absolute() and (root / t).is_dir()):
            raise DirgeError(f"refusing to walk directory: {t}", 2)
        wanted.add(t)
    return wanted


def format_human(report: DirgeReport, *, repo: Path, base: str) -> str:
    name = repo.name or str(repo)
    d = report.delta
    lines = [
        f"# dirge overlay onto {base}  ({name})",
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
    lines.append("dirge  (exclusive-A forks that would die; sibling arms clustered)")
    if report.covering:
        for o in report.covering:
            kinds = "/".join(o.kinds)
            lines.append(f"  A   exclusive_a  {o.label}")
            n = len(o.paths_a)
            files = f"{n} file" + ("" if n == 1 else "s")
            lines.append(
                f"           {files}  depth={o.depth}  arms={o.arm_n}  {kinds}"
            )
            if o.arm_n > 1:
                for s in o.arms_listed:
                    lines.append(f"             · {s.label}")
            if o.holders_a:
                lines.append("           holders A: " + ", ".join(o.holders_a[:6]))
            pin = o.pin_for_true()
            if pin:
                lines.append(f"           pin  {pin[0]}:{pin[1]}")
    else:
        lines.append("  (empty — nothing died)")
    if d.unplaced:
        lines.append("")
        lines.append("unplaced  " + ", ".join(d.unplaced[:6]))
    lines.append(
        f"dirge={len(report.covering)}  deaths={report.death_n}  "
        f"born={report.born_n}  moves={report.move_n}  arms={report.arm_n}"
    )
    return "\n".join(lines)


def format_tsv(report: DirgeReport) -> str:
    rows = []
    for o in report.covering:
        pin = o.pin_for_true()
        path = pin[0] if pin else (o.paths_a[0] if o.paths_a else "")
        line = pin[1] if pin else 0
        rows.append("\t".join(["A", o.role, o.label, path, str(line), str(o.arm_n)]))
    return "\n".join(rows)


def format_oneline(report: DirgeReport) -> str:
    return "\n".join(f"A\t{o.label}\tarms={o.arm_n}" for o in report.covering)


def format_json(report: DirgeReport, *, repo: Path, base: str) -> str:
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
            "dirge": [o.to_record() for o in report.covering],
            "deaths": report.death_n,
            "born": report.born_n,
            "moves": report.move_n,
            "arms": report.arm_n,
            "unplaced": d.unplaced,
        },
        indent=2,
        ensure_ascii=False,
    )


def selftest() -> int:
    from .overlay import apply_hunks, parse_unified_diff
    from .stacks import Stack, cluster_siblings, cond_label, dead_cover, stacks_in_source

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
    labels = [" | ".join(f"{k} {p}".strip() for k, p in key) for key in keys]
    check(
        "ready given + x>0 is a stack",
        any("x > 0" in lab or "x>0" in lab.replace(" ", "") for lab in labels),
    )

    river_if = Stack(
        key=(("if", "flow_score > 0.2"),),
        holders_a=["src/river.py"],
        holders_b=[],
        paths_a=["src/river.py"],
        paths_b=[],
        pin_a=("src/river.py", 2),
        pin_b=None,
        fn="bar_color",
    )
    river_elif = Stack(
        key=(("elif", "flow_score < -0.2"),),
        holders_a=["src/river.py"],
        holders_b=[],
        paths_a=["src/river.py"],
        paths_b=[],
        pin_a=("src/river.py", 4),
        pin_b=None,
        fn="bar_color",
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
    clustered = cluster_siblings([river_if, river_elif])
    check("if/elif cluster as one", len(clustered) == 1 and len(clustered[0]) == 2)
    dead = dead_cover([river_if, river_elif, *flood, move, tick], ["src/river.py"], limit=4)
    check("dead cover one obituary not two sibling rows", len(dead) == 1)
    check("obituary keeps both arms", dead[0].arm_n == 2)
    check("dead cover ignores exclusive-B flood", all(o.true_on == "A" for o in dead))
    check("dead cover ignores the move", all(o.role != "move" for o in dead))
    check(
        "default leftover ignores surviving-file exclusive-A",
        all(o.lead.key != tick.key for o in dead),
    )
    dead2 = dead_cover(
        [river_if, river_elif, tick], ["src/river.py"], limit=6, also_changed=True
    )
    check(
        "--also-changed includes surviving-file exclusive-A",
        any(o.lead.key == tick.key or any(m.key == tick.key for m in o.members) for o in dead2),
    )

    seq_if = Stack(
        key=(("if", "app.flowScore > 0.2"),),
        holders_a=["row.swift"],
        holders_b=[],
        paths_a=["row.swift"],
        paths_b=[],
        pin_a=("row.swift", 4),
        pin_b=None,
        fn="Color",
    )
    seq_seq = Stack(
        key=(("given", "¬(app.flowScore > 0.2)"), ("if", "app.flowScore < -0.2")),
        holders_a=["row.swift"],
        holders_b=[],
        paths_a=["row.swift"],
        paths_b=[],
        pin_a=("row.swift", 8),
        pin_b=None,
        fn="Color",
    )
    seq_else = Stack(
        key=(
            ("given", "¬(app.flowScore > 0.2)"),
            ("given", "¬(app.flowScore < -0.2)"),
        ),
        holders_a=["row.swift"],
        holders_b=[],
        paths_a=["row.swift"],
        paths_b=[],
        pin_a=("row.swift", 9),
        pin_b=None,
        fn="Color",
    )
    seq_elif = Stack(
        key=(("elif", "app.flowScore < -0.2"),),
        holders_a=["row.swift"],
        holders_b=[],
        paths_a=["row.swift"],
        paths_b=[],
        pin_a=("row.swift", 6),
        pin_b=None,
        fn="Color",
    )
    seq_groups = cluster_siblings([seq_if, seq_seq, seq_else, seq_elif])
    check(
        "sequential if + elif + given-else are one obituary",
        len(seq_groups) == 1 and len(seq_groups[0]) == 4,
    )
    from .stacks import Obituary

    seq_obit = Obituary(members=seq_groups[0], only_a={"row.swift"})
    check(
        "obituary lead is the root true-arm, not the sequential given",
        seq_obit.label == "if app.flowScore > 0.2",
    )
    check(
        "obituary pin is the true-arm pin",
        seq_obit.pin_for_true() == ("row.swift", 4),
    )

    a_if = Stack(
        key=(("if", "a > 0"),),
        holders_a=["two.py"],
        holders_b=[],
        paths_a=["two.py"],
        paths_b=[],
        pin_a=("two.py", 2),
        pin_b=None,
        fn="classify",
    )
    b_elif = Stack(
        key=(("elif", "b > 0"),),
        holders_a=["two.py"],
        holders_b=[],
        paths_a=["two.py"],
        paths_b=[],
        pin_a=("two.py", 4),
        pin_b=None,
        fn="classify",
    )
    c_if = Stack(
        key=(("if", "c > 0"),),
        holders_a=["two.py"],
        holders_b=[],
        paths_a=["two.py"],
        paths_b=[],
        pin_a=("two.py", 6),
        pin_b=None,
        fn="classify",
    )
    d_elif = Stack(
        key=(("elif", "d > 0"),),
        holders_a=["two.py"],
        holders_b=[],
        paths_a=["two.py"],
        paths_b=[],
        pin_a=("two.py", 8),
        pin_b=None,
        fn="classify",
    )
    two = cluster_siblings([a_if, b_elif, c_if, d_elif])
    check("independent if-chains stay two obituaries", len(two) == 2)
    check("each chain keeps its elif", all(len(g) == 2 for g in two))

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
            raise DirgeError("diff named no files", 2)
        report = dirge_from_images(
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
    except DirgeError as exc:
        print(f"dirge: {exc}", file=sys.stderr)
        return exc.code


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        return run(argv)
    except KeyboardInterrupt:
        print("dirge: interrupted", file=sys.stderr)
        return 130
