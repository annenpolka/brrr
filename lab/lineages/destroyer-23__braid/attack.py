#!/usr/bin/env python3
"""DESTROYER battery for braid — occupancy of the composed after-image.

Do not re-run DESTROYER_PLAIT COMMUTE/JAM/ECHO-as-image wholesale.
Attack the fold: one occupancy of the union/series after-image, not plait's
schedule table and not hank --emit.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

BRAID = os.environ.get(
    "BRAID",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cbac00204512/braid",
)
PLEA = os.environ.get(
    "PLEA",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b0f-7ef0-76c0-9975-2d17551b311f/plea",
)
HANK = os.environ.get(
    "HANK",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10aab0ac23cc/hank",
)
QUIRE = os.environ.get(
    "QUIRE",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7d97e1cbfdad/quire",
)
VICTIM = Path(BRAID).resolve().parent
SITBONE = Path(
    os.environ.get("SITBONE", "/Users/annenpolka/ghq/github.com/annenpolka/sitbone")
)
ROOT = Path(os.environ.get("DESTROY_ROOT", "/tmp/destroy-braid"))
FIX = ROOT / "fixtures"
TREE = ROOT / "trees"
LOG = ROOT / "transcript.txt"

transcript: list[str] = []


def log(msg: str = "") -> None:
    print(msg, flush=True)
    transcript.append(msg)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def jlines(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def run(
    args: list[str],
    stdin: bytes | str | None = None,
    cwd: str | None = None,
    timeout: float = 30.0,
    bin: str | None = None,
) -> tuple[int, str, str, float]:
    cmd = [bin or BRAID, *args]
    if stdin is None:
        data = None
    elif isinstance(stdin, bytes):
        data = stdin
    else:
        data = stdin.encode("utf-8")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            cmd,
            input=data,
            capture_output=True,
            cwd=cwd,
            timeout=timeout,
        )
        elapsed = time.perf_counter() - t0
        out = p.stdout.decode("utf-8", errors="replace")
        err = p.stderr.decode("utf-8", errors="replace")
        return p.returncode, out, err, elapsed
    except subprocess.TimeoutExpired as e:
        elapsed = time.perf_counter() - t0
        out = (e.stdout or b"").decode("utf-8", errors="replace")
        err = (e.stderr or b"").decode("utf-8", errors="replace") + f"\nTIMEOUT after {timeout}s"
        return 124, out, err, elapsed
    except FileNotFoundError as e:
        return 127, "", str(e), 0.0


def banner(title: str) -> None:
    log()
    log("=" * 72)
    log(title)
    log("=" * 72)


def show(rc: int, out: str, err: str, elapsed: float, max_out: int = 1800) -> None:
    log(f"# rc={rc}  elapsed={elapsed:.3f}s")
    if out:
        text = out if len(out) <= max_out else out[:max_out] + "\n…[truncated]…"
        log(text.rstrip())
    if err:
        text = err if len(err) <= 600 else err[:600] + "\n…[stderr truncated]…"
        log("STDERR: " + text.rstrip())


def jload(text: str) -> dict:
    return json.loads(text)


def occupy_bits(js: dict) -> str:
    composed = js.get("composed") or []
    bits = []
    for c in composed:
        occ = c.get("occupancy") or {}
        bits.append(
            f"{c.get('path')} compose={c.get('verdict')} covering={c.get('covering')} "
            f"span={c.get('start')}-{c.get('end')} fate={occ.get('fate')} "
            f"method={occ.get('method')} before={c.get('before')!r} after={c.get('after')!r}"
        )
    return (
        f"compose={js.get('compose')} occupy={js.get('occupy')} occupied={js.get('occupied')} "
        f"n={js.get('n')} files={js.get('files')} method={js.get('method')}\n  "
        + "\n  ".join(bits)
    )


def copy_victim_gold() -> None:
    src_fix = VICTIM / "fixtures"
    dst = FIX / "victim"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src_fix, dst)


def build_fixtures() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    TREE.mkdir(parents=True, exist_ok=True)

    # STACK three-way: v1→v2→v3→v4, inverted clocks on the last hop.
    write(
        FIX / "stack-three.jsonl",
        jlines(
            [
                {
                    "id": "r1",
                    "path": "app.py",
                    "start_line": 2,
                    "line": 2,
                    "before": ["v1"],
                    "after": ["v2"],
                    "original_commit_id": "c1",
                    "created_at": "2020-01-03T00:00:00Z",
                },
                {
                    "id": "r2",
                    "path": "app.py",
                    "start_line": 2,
                    "line": 2,
                    "before": ["v2"],
                    "after": ["v3"],
                    "original_commit_id": "c2",
                    "created_at": "2020-01-02T00:00:00Z",
                },
                {
                    "id": "r3",
                    "path": "app.py",
                    "start_line": 2,
                    "line": 2,
                    "before": ["v3"],
                    "after": ["v4"],
                    "original_commit_id": "c3",
                    "created_at": "2020-01-01T00:00:00Z",
                },
            ]
        ),
    )
    write(TREE / "stack3-origin" / "app.py", "alpha\nv1\ngamma\n")
    write(TREE / "stack3-r1" / "app.py", "alpha\nv2\ngamma\n")
    write(TREE / "stack3-r2" / "app.py", "alpha\nv3\ngamma\n")
    write(TREE / "stack3-final" / "app.py", "alpha\nv4\ngamma\n")
    write(TREE / "stack3-both-v1-v2" / "app.py", "alpha\nv1\nv2\ngamma\n")

    # Covering window: commute pair with a live unclaimed middle.
    write(
        FIX / "window-commute.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha"],
                    "after": ["ALPHA"],
                },
                {
                    "id": "bob",
                    "path": "app.py",
                    "start_line": 3,
                    "line": 3,
                    "before": ["gamma"],
                    "after": ["GAMMA"],
                },
            ]
        ),
    )
    write(TREE / "window-origin" / "app.py", "alpha\nbeta\ngamma\n")
    write(TREE / "window-drift-mid" / "app.py", "alpha\nBETA\ngamma\n")
    write(TREE / "window-drift-comment" / "app.py", "alpha\n# reviewer nattered\ngamma\n")
    write(TREE / "window-a-only" / "app.py", "ALPHA\nbeta\ngamma\n")
    write(TREE / "window-a-only-drift" / "app.py", "ALPHA\nBETA\ngamma\n")
    write(TREE / "window-pad1" / "app.py", "PAD\nalpha\nbeta\ngamma\n")
    write(TREE / "window-pad3" / "app.py", "P1\nP2\nP3\nalpha\nbeta\ngamma\n")
    write(TREE / "window-pad5" / "app.py", "P1\nP2\nP3\nP4\nP5\nalpha\nbeta\ngamma\n")
    write(TREE / "window-wide" / "app.py", "alpha\nbeta\ngamma\nEXTRA\n")

    # Distant commute: 10-line gap so covering is fat.
    write(
        FIX / "window-far.jsonl",
        jlines(
            [
                {
                    "id": "top",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["L1"],
                    "after": ["T1"],
                },
                {
                    "id": "bot",
                    "path": "app.py",
                    "start_line": 12,
                    "line": 12,
                    "before": ["L12"],
                    "after": ["T12"],
                },
            ]
        ),
    )
    far = [f"L{i}" for i in range(1, 13)]
    write(TREE / "far-origin" / "app.py", "\n".join(far) + "\n")
    far_drift = list(far)
    far_drift[5] = "L6-DRIFT"  # unclaimed line 6
    write(TREE / "far-drift" / "app.py", "\n".join(far_drift) + "\n")
    far_shift = ["PAD"] + far  # whole block down 1
    write(TREE / "far-shift1" / "app.py", "\n".join(far_shift) + "\n")
    far_shift10 = ["PAD"] * 10 + far
    write(TREE / "far-shift10" / "app.py", "\n".join(far_shift10) + "\n")

    # NFC / NFD paths and line images.
    nfc_path = "café.py"
    nfd_path = "cafe\u0301.py"
    nfc_word = "café"
    nfd_word = "cafe\u0301"
    write(
        FIX / "nfc-two-paths.jsonl",
        jlines(
            [
                {
                    "id": "nfc",
                    "path": nfc_path,
                    "start_line": 1,
                    "line": 1,
                    "before": ["x"],
                    "after": ["y"],
                },
                {
                    "id": "nfd",
                    "path": nfd_path,
                    "start_line": 3,
                    "line": 3,
                    "before": ["p"],
                    "after": ["q"],
                },
            ]
        ),
    )
    write(
        FIX / "nfc-content.jsonl",
        jlines(
            [
                {
                    "id": "sip",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": [nfc_word],
                    "after": ["tea"],
                }
            ]
        ),
    )
    write(
        FIX / "nfd-content.jsonl",
        jlines(
            [
                {
                    "id": "sip",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": [nfd_word],
                    "after": ["tea"],
                }
            ]
        ),
    )
    write(TREE / "nfc-file" / nfc_path, "x\nmiddle\np\n")
    write(TREE / "nfd-file" / nfd_path, "x\nmiddle\np\n")
    write(TREE / "nfc-word" / "app.py", nfc_word + "\n")
    write(TREE / "nfd-word" / "app.py", nfd_word + "\n")

    # Remarks MIXED / COVER on the commute file.
    write(
        FIX / "remarks-cover.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha"],
                    "after": ["ALPHA"],
                    "body": "```suggestion\nALPHA\n```",
                },
                {
                    "id": "bob",
                    "path": "app.py",
                    "start_line": 3,
                    "line": 3,
                    "before": ["gamma"],
                    "after": ["GAMMA"],
                    "body": "```suggestion\nGAMMA\n```",
                },
                {
                    "id": "nit",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "body": "lgtm but also this line",
                },
            ]
        ),
    )
    write(
        FIX / "remarks-thread.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha"],
                    "after": ["ALPHA"],
                },
                {
                    "id": "note",
                    "path": "util.py",
                    "line": 1,
                    "body": "please extract this",
                },
                {
                    "id": "reply",
                    "path": "util.py",
                    "line": 1,
                    "body": "will do",
                    "in_reply_to_id": "note",
                },
            ]
        ),
    )
    write(TREE / "two-file" / "app.py", "alpha\nbeta\ngamma\n")
    write(TREE / "two-file" / "util.py", "please extract this\n")

    # Empty-before markdown + same-line empty-before two afters.
    write(
        FIX / "md-empty-same-line.md",
        "app.py:2-2\n```suggestion\nHELLO world\n```\n\n"
        "app.py:2-2\n```suggestion\nhello WORLD\n```\n",
    )
    write(
        FIX / "md-empty-disjoint.md",
        "app.py:1-1\n```suggestion\nALPHA\n```\n\n"
        "app.py:3-3\n```suggestion\nGAMMA\n```\n",
    )
    write(TREE / "md-wrong-canvas" / "app.py", "XXX\nYYY\nZZZ\n")
    write(TREE / "md-already-alpha" / "app.py", "ALPHA\nbeta\ngamma\n")

    # Replacement-as-union (plait hole, confirm braid refuses occupy).
    write(
        FIX / "replace-words.jsonl",
        jlines(
            [
                {
                    "id": "left",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["hello world"],
                    "after": ["HELLO world"],
                },
                {
                    "id": "right",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["hello world"],
                    "after": ["hello WORLD"],
                },
            ]
        ),
    )
    write(TREE / "hello" / "app.py", "hello world\n")

    # Inverted-clock stack both-images (plait same-tree lie).
    write(
        FIX / "invert-stack.jsonl",
        jlines(
            [
                {
                    "id": "round1",
                    "path": "app.py",
                    "start_line": 2,
                    "line": 2,
                    "before": ["beta"],
                    "after": ["beta2"],
                    "original_commit_id": "c1",
                    "created_at": "2020-01-02T00:00:00Z",
                },
                {
                    "id": "round2",
                    "path": "app.py",
                    "start_line": 2,
                    "line": 2,
                    "before": ["beta2"],
                    "after": ["beta3"],
                    "original_commit_id": "c2",
                    "created_at": "2020-01-01T00:00:00Z",
                },
            ]
        ),
    )
    write(TREE / "stack-origin" / "app.py", "alpha\nbeta\ngamma\n")
    write(TREE / "stack-mid" / "app.py", "alpha\nbeta2\ngamma\n")
    write(TREE / "stack-after" / "app.py", "alpha\nbeta3\ngamma\n")
    write(TREE / "stack-both" / "app.py", "alpha\nbeta\nbeta2\ngamma\n")
    write(TREE / "stack-neighbors-drift" / "app.py", "ALPHA\nbeta\nGAMMA\n")

    # Multi-file COMMUTE: occupy per path, MIXED if one landed.
    write(
        FIX / "two-file.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha"],
                    "after": ["ALPHA"],
                },
                {
                    "id": "carol",
                    "path": "util.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["gamma"],
                    "after": ["GAMMA"],
                },
            ]
        ),
    )
    write(TREE / "two-origin" / "app.py", "alpha\nbeta\n")
    write(TREE / "two-origin" / "util.py", "gamma\ndelta\n")
    write(TREE / "two-a-only" / "app.py", "ALPHA\nbeta\n")
    write(TREE / "two-a-only" / "util.py", "gamma\ndelta\n")
    write(TREE / "two-missing-util" / "app.py", "alpha\nbeta\n")

    # Subset mid-state (insert landed, return 1 leftover).
    write(
        FIX / "subset.jsonl",
        (VICTIM / "fixtures" / "stack-subset.jsonl").read_text(encoding="utf-8"),
    )
    write(TREE / "subset-origin" / "app.py", "pass\n")
    write(TREE / "subset-mid" / "app.py", "def f():\n    return 1\n\n")
    write(TREE / "subset-final" / "app.py", "def f():\n    return 2\n\n")

    # Locus slack on a 1-line STACK fold.
    write(TREE / "stack-shift2" / "app.py", "pad\npad\nalpha\nbeta\ngamma\n")
    write(TREE / "stack-shift3" / "app.py", "pad\npad\npad\nalpha\nbeta\ngamma\n")

    # DUPLEX: covering before and after both live as independent blocks.
    write(TREE / "duplex" / "app.py", "alpha\nbeta\ngamma\nALPHA\nbeta\nGAMMA\n")

    # Whitespace-only drift of claimed line.
    write(
        FIX / "ws-claim.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha"],
                    "after": ["ALPHA"],
                },
                {
                    "id": "bob",
                    "path": "app.py",
                    "start_line": 3,
                    "line": 3,
                    "before": ["gamma"],
                    "after": ["GAMMA"],
                },
            ]
        ),
    )
    write(TREE / "ws-trail" / "app.py", "alpha  \nbeta\ngamma\n")

    # Ignore-space occupy (compose vs occupy).
    write(
        FIX / "ws-before.jsonl",
        jlines(
            [
                {
                    "id": "alice",
                    "path": "app.py",
                    "start_line": 1,
                    "line": 1,
                    "before": ["alpha  "],
                    "after": ["ALPHA"],
                },
                {
                    "id": "bob",
                    "path": "app.py",
                    "start_line": 3,
                    "line": 3,
                    "before": ["gamma"],
                    "after": ["GAMMA"],
                },
            ]
        ),
    )

    # New-file insert occupy (missing path).
    write(
        FIX / "new-file.jsonl",
        jlines(
            [
                {
                    "id": "create",
                    "path": "new.py",
                    "start_line": 1,
                    "line": 1,
                    "before": [],
                    "after": ["print(1)"],
                }
            ]
        ),
    )


def section_selftest() -> None:
    banner("0. victim selftest / demo / no --emit")
    rc, out, err, el = run(["--selftest"])
    show(rc, out, err, el)
    log(f"selftest rc={rc} (want 0)")
    rc, out, err, el = run(["--version"])
    show(rc, out, err, el)
    rc, out, err, el = run(["--help"])
    log("--help mentions emit: " + str("emit" in (out + err).lower()))
    rc, out, err, el = run(["--emit"])
    show(rc, out, err, el)
    log(f"--emit rc={rc} (hank's verb; braid should argparse-fail)")


def section_stack_mid() -> None:
    banner("1. STACK mid-state: APPLIED-of-round-1 vs SUPERSEDED-of-beta3")
    gold = VICTIM / "fixtures" / "stack.jsonl"
    for name, tree in [
        ("origin", VICTIM / "fixtures" / "trees" / "stack"),
        ("mid", VICTIM / "fixtures" / "trees" / "stack-mid"),
        ("after", VICTIM / "fixtures" / "trees" / "stack-after"),
        ("both", VICTIM / "fixtures" / "trees" / "stack-both"),
    ]:
        rc, out, err, el = run(["--json", "-C", str(tree), str(gold)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- braid stack-{name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        if Path(PLEA).is_file():
            prc, pout, perr, pel = run(
                ["--json", "--worktree", "-C", str(tree), str(gold)], bin=PLEA
            )
            log(f"--- plea stack-{name} rc={prc} ---")
            if pout.strip().startswith("{") or pout.strip().startswith("["):
                try:
                    pj = json.loads(pout)
                    log(json.dumps(pj, indent=2)[:1600])
                except json.JSONDecodeError:
                    log(pout[:1600])
            else:
                show(prc, pout, perr, pel)

    # three-way inverted clock
    for name in ["stack3-origin", "stack3-r1", "stack3-r2", "stack3-final", "stack3-both-v1-v2"]:
        rc, out, err, el = run(
            ["--json", "-C", str(TREE / name), str(FIX / "stack-three.jsonl")]
        )
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- three-way {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        if Path(PLEA).is_file():
            prc, pout, perr, pel = run(
                ["--json", "--worktree", "-C", str(TREE / name), str(FIX / "stack-three.jsonl")],
                bin=PLEA,
            )
            log(f"plea {name} rc={prc}")
            if pout.strip()[:1] in "{[":
                try:
                    log(json.dumps(json.loads(pout), indent=2)[:1200])
                except json.JSONDecodeError:
                    log(pout[:800])


def section_window_drift() -> None:
    banner("2. covering window drift — unclaimed gap / locus slack")
    stream = FIX / "window-commute.jsonl"
    for name in [
        "window-origin",
        "window-drift-mid",
        "window-drift-comment",
        "window-a-only",
        "window-a-only-drift",
        "window-pad1",
        "window-pad3",
        "window-pad5",
        "window-wide",
        "ws-trail",
        "duplex",
    ]:
        rc, out, err, el = run(["--json", "-C", str(TREE / name), str(stream)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)

    far = FIX / "window-far.jsonl"
    for name in ["far-origin", "far-drift", "far-shift1", "far-shift10"]:
        rc, out, err, el = run(["--json", "-C", str(TREE / name), str(far)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)

    # STACK covering is 1-line: neighbor drift should stay PENDING of the fold
    gold = FIX / "invert-stack.jsonl"
    rc, out, err, el = run(
        ["--json", "-C", str(TREE / "stack-neighbors-drift"), str(gold)]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- STACK neighbor drift (ALPHA/beta/GAMMA) ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    for name in ["stack-shift2", "stack-shift3"]:
        rc, out, err, el = run(["--json", "-C", str(TREE / name), str(gold)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- STACK {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)

    # cli/cli PR #7 covering drift of one unclaimed line in the 54-line window
    cli_stream = VICTIM / "fixtures" / "cli-pr7.json"
    cli_tree = VICTIM / "fixtures" / "trees" / "cli-orig"
    rc, out, err, el = run(["--json", "-C", str(cli_tree), str(cli_stream)])
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- cli orig covering ---")
    show(rc, occupy_bits(js) if js else out, err, el, max_out=2500)
    if js.get("composed"):
        c0 = js["composed"][0]
        log(
            f"cli covering lines={None if c0.get('before') is None else len(c0.get('before') or [])} "
            f"start={c0.get('start')} end={c0.get('end')} covering={c0.get('covering')}"
        )
    drifted = TREE / "cli-drift"
    if (cli_tree / "command" / "pr.go").is_file():
        shutil.copytree(cli_tree, drifted, dirs_exist_ok=True)
        p = drifted / "command" / "pr.go"
        text = p.read_text(encoding="utf-8")
        # Change an unclaimed line inside @347-400 (the TODO at 363).
        text2 = text.replace(
            "// TODO: figure out a less ridiculous way to parse GraphQL response",
            "// TODO: drifted comment inside the covering window",
            1,
        )
        p.write_text(text2, encoding="utf-8")
        rc, out, err, el = run(["--json", "-C", str(drifted), str(cli_stream)])
        js = jload(out) if out.strip().startswith("{") else {}
        log("--- cli window-drift (TODO inside @347-400) ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        # nits still open: the two return lines unchanged
        src = (drifted / "command" / "pr.go").read_text(encoding="utf-8")
        log(
            "nit347 still live: "
            + str("return &github.PullRequest{}, err" in src)
        )
        log(
            "nit400 still live: "
            + str(
                "return &graphqlPullRequest{}, []graphqlPullRequest{}, []graphqlPullRequest{}, err"
                in src
            )
        )


def section_nfc() -> None:
    banner("3. NFC café paths / line images")
    log(f"nfc path {unicodedata.normalize('NFC', 'café.py')!r}")
    log(f"nfd path {unicodedata.normalize('NFD', 'café.py')!r}")
    nfc_dir = TREE / "nfc-file"
    nfd_dir = TREE / "nfd-file"
    # inode identity on APFS
    nfc_p = nfc_dir / "café.py"
    nfd_p = nfd_dir / "cafe\u0301.py"
    log(f"nfc exists={nfc_p.exists()} nfd exists={nfd_p.exists()}")
    if nfc_p.exists() and nfd_p.exists():
        log(f"same inode? nfc={nfc_p.stat().st_ino} nfd={nfd_p.stat().st_ino}")
        # Can we see the other normalization in each dir?
        log(f"nfc-dir sees NFD name: {(nfc_dir / 'café.py').exists()}")
        log(f"nfd-dir sees NFC name: {(nfd_dir / 'café.py').exists()}")

    rc, out, err, el = run(["--json", "--report-only", str(FIX / "nfc-two-paths.jsonl")])
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- two path keys no tree ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    if js.get("strands"):
        log("strand paths: " + repr([s.get("path") for s in js["strands"]]))

    for tree in [nfc_dir, nfd_dir]:
        rc, out, err, el = run(
            ["--json", "-C", str(tree), str(FIX / "nfc-two-paths.jsonl")]
        )
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- two-paths vs {tree.name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)

    for stream, tree in [
        (FIX / "nfc-content.jsonl", TREE / "nfc-word"),
        (FIX / "nfc-content.jsonl", TREE / "nfd-word"),
        (FIX / "nfd-content.jsonl", TREE / "nfc-word"),
        (FIX / "nfd-content.jsonl", TREE / "nfd-word"),
    ]:
        rc, out, err, el = run(["--json", "-C", str(tree), str(stream)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- {stream.name} vs {tree.name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)


def section_remarks() -> None:
    banner("4. remarks MIXED / COVER — occupy of the suggestion fold")
    cli = VICTIM / "fixtures" / "cli-pr7.json"
    cli_tree = VICTIM / "fixtures" / "trees" / "cli-orig"
    rc, out, err, el = run(
        ["--json", "--remarks", "-C", str(cli_tree), str(cli)]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- cli-pr7 --remarks ---")
    show(rc, occupy_bits(js) if js else out, err, el, max_out=2500)
    if js:
        log(
            f"components={json.dumps(js.get('component_counts') or js.get('components'), default=str)[:800]}"
        )
        log(f"compose={js.get('compose')} occupy={js.get('occupy')} n={js.get('n')}")

    rc, out, err, el = run(
        ["--json", "--remarks", "-C", str(TREE / "window-origin"), str(FIX / "remarks-cover.jsonl")]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- commute + same-locus remark COVER ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    if js:
        log("pairs: " + json.dumps(js.get("pairs"), ensure_ascii=False)[:1200])
        log("components: " + json.dumps(js.get("components"), ensure_ascii=False)[:1200])

    rc, out, err, el = run(
        [
            "--json",
            "--remarks",
            "-C",
            str(TREE / "two-file"),
            str(FIX / "remarks-thread.jsonl"),
        ]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- suggestion + other-file THREAD → MIXED header ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    if js:
        log("components: " + json.dumps(js.get("components"), ensure_ascii=False)[:1200])


def section_empty_before() -> None:
    banner("5. empty-before: not SPLIT on disjoint; occupy of a live canvas")
    victim_md = VICTIM / "fixtures" / "md-commute-noquote.md"
    rc, out, err, el = run(
        ["--json", "-C", str(VICTIM / "fixtures" / "trees" / "commute"), str(victim_md)]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- victim md-commute-noquote vs commute tree ---")
    show(rc, occupy_bits(js) if js else out, err, el)

    rc, out, err, el = run(["--json", "--report-only", str(FIX / "md-empty-same-line.md")])
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- same-line empty-before two afters (word commute?) ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    log(f"rc={rc} compose={js.get('compose') if js else None}")

    rc, out, err, el = run(
        ["--json", "-C", str(TREE / "hello"), str(FIX / "md-empty-same-line.md")]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- same-line empty-before against hello world tree ---")
    show(rc, occupy_bits(js) if js else out, err, el)

    for name in ["window-origin", "md-wrong-canvas", "md-already-alpha"]:
        rc, out, err, el = run(
            ["--json", "-C", str(TREE / name), str(FIX / "md-empty-disjoint.md")]
        )
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- md-empty-disjoint vs {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)


def section_replacement() -> None:
    banner("6. replacement-as-union — occupy refused")
    for stream in [
        FIX / "replace-words.jsonl",
        VICTIM / "fixtures" / "same-line-overlap-same-after.jsonl",
        VICTIM / "fixtures" / "same-line-split.jsonl",
        VICTIM / "fixtures" / "jam.jsonl",
        VICTIM / "fixtures" / "split.jsonl",
    ]:
        rc, out, err, el = run(["--json", "--report-only", str(stream)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- {stream.name} ---")
        if js:
            log(
                f"rc={rc} compose={js.get('compose')} occupy={js.get('occupy')} "
                f"occupied={js.get('occupied')} composed={js.get('composed')}"
            )
        else:
            show(rc, out, err, el)
        rc2, out2, err2, el2 = run(["-C", str(TREE / "hello"), str(stream)])
        log(f"pretty rc={rc2} occupy-line: " + (out2.splitlines()[0] if out2 else "(empty)"))
        if "occupy=" in out2:
            log(out2.splitlines()[0])


def section_inverted_clock() -> None:
    banner("7. inverted-clock same-tree — fold, not schedule table")
    stream = FIX / "invert-stack.jsonl"
    for name in ["stack-origin", "stack-mid", "stack-after", "stack-both"]:
        rc, out, err, el = run(["--json", "-C", str(TREE / name), str(stream)])
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- invert {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        pretty, _, _, _ = run(["-C", str(TREE / name), str(stream)])
        # confirm no same-tree / line= / time= / topo= witness table
        head = pretty[1] if False else (pretty[0] if False else "")
        joined = pretty if isinstance(pretty, str) else ""
    rc, out, err, el = run(["-C", str(TREE / "stack-both"), str(stream)])
    log("--- invert stack-both pretty (must not say same-tree) ---")
    show(rc, out, err, el)
    log("has same-tree: " + str("same-tree" in out))
    log("has apply:line: " + str("apply:line" in out))


def section_multifile_subset_emit() -> None:
    banner("8. multi-file occupy MIXED / subset mid / no emit / hank contrast")
    for name in ["two-origin", "two-a-only", "two-missing-util"]:
        rc, out, err, el = run(
            ["--json", "-C", str(TREE / name), str(FIX / "two-file.jsonl")]
        )
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- braid two-file {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        if Path(QUIRE).is_file():
            qrc, qout, qerr, qel = run(
                ["--json", "-C", str(TREE / name), str(FIX / "two-file.jsonl")],
                bin=QUIRE,
            )
            log(f"quire {name} rc={qrc}")
            if qout.strip()[:1] in "{[":
                try:
                    qj = json.loads(qout)
                    log(
                        f"quire compose={qj.get('compose')} occupy={qj.get('occupy')} "
                        f"image={qj.get('image')}"
                    )
                except json.JSONDecodeError:
                    log(qout[:400])

    for name in ["subset-origin", "subset-mid", "subset-final"]:
        rc, out, err, el = run(
            ["--json", "-C", str(TREE / name), str(FIX / "subset.jsonl")]
        )
        js = jload(out) if out.strip().startswith("{") else {}
        log(f"--- subset {name} ---")
        show(rc, occupy_bits(js) if js else out, err, el)
        if Path(PLEA).is_file():
            prc, pout, perr, pel = run(
                ["--json", "--worktree", "-C", str(TREE / name), str(FIX / "subset.jsonl")],
                bin=PLEA,
            )
            log(f"plea subset {name} rc={prc}")
            if pout.strip()[:1] in "{[":
                try:
                    log(json.dumps(json.loads(pout), indent=2)[:1000])
                except json.JSONDecodeError:
                    log(pout[:600])

    rc, out, err, el = run(["--json", str(FIX / "new-file.jsonl")])
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- new-file no -C ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    rc, out, err, el = run(
        ["--json", "-C", str(TREE / "window-origin"), str(FIX / "new-file.jsonl")]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- new-file vs tree missing new.py ---")
    show(rc, occupy_bits(js) if js else out, err, el)

    if Path(HANK).is_file():
        rc, out, err, el = run(
            [
                "--emit",
                "-C",
                str(VICTIM / "fixtures" / "trees" / "stack"),
                str(VICTIM / "fixtures" / "stack.jsonl"),
            ],
            bin=HANK,
        )
        log("--- hank --emit of STACK fold (not braid) ---")
        show(rc, out, err, el)


def section_sitbone() -> None:
    banner("9. sitbone dogfood (only if a real suggestion stream exists)")
    if not SITBONE.is_dir():
        log("sitbone missing; skip")
        return
    hits = []
    for p in SITBONE.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in {".md", ".swift", ".json", ".txt"}:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "```suggestion" in text:
            hits.append(str(p))
    log(f"sitbone ```suggestion files: {hits[:8]} count={len(hits)}")
    # Synthetic occupancy against PresenceArbiter.swift: two commuting nits
    # on a real sitbone file (covering window of a production source).
    arb = SITBONE / "Sources" / "SitboneCore" / "PresenceArbiter.swift"
    if not arb.is_file():
        log("PresenceArbiter.swift missing; skip")
        return
    lines = arb.read_text(encoding="utf-8").splitlines()
    # pick two non-adjacent short lines
    picks = []
    for i, ln in enumerate(lines, 1):
        if ln.strip() and not ln.strip().startswith("//") and 8 < i < 80:
            picks.append((i, ln))
        if len(picks) >= 8:
            break
    if len(picks) < 4:
        log("not enough sitbone lines")
        return
    a_i, a_ln = picks[0]
    b_i, b_ln = picks[3]
    stream = FIX / "sitbone-window.jsonl"
    write(
        stream,
        jlines(
            [
                {
                    "id": "a",
                    "path": "Sources/SitboneCore/PresenceArbiter.swift",
                    "start_line": a_i,
                    "line": a_i,
                    "before": [a_ln],
                    "after": [a_ln + " // nit-a"],
                },
                {
                    "id": "b",
                    "path": "Sources/SitboneCore/PresenceArbiter.swift",
                    "start_line": b_i,
                    "line": b_i,
                    "before": [b_ln],
                    "after": [b_ln + " // nit-b"],
                },
            ]
        ),
    )
    rc, out, err, el = run(["--json", "-C", str(SITBONE), str(stream)])
    js = jload(out) if out.strip().startswith("{") else {}
    log(f"--- sitbone covering @{a_i}×@{b_i} ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    if js.get("composed"):
        c0 = js["composed"][0]
        log(
            f"sitbone covering={c0.get('covering')} span={c0.get('start')}-{c0.get('end')} "
            f"n_before={len(c0.get('before') or [])}"
        )
    # drift an unclaimed line inside the window
    drifted = TREE / "sitbone-drift"
    rel = Path("Sources/SitboneCore/PresenceArbiter.swift")
    (drifted / rel).parent.mkdir(parents=True, exist_ok=True)
    dlines = list(lines)
    mid = (a_i + b_i) // 2
    if 1 <= mid <= len(dlines):
        dlines[mid - 1] = dlines[mid - 1] + " // window-drift"
    (drifted / rel).write_text("\n".join(dlines) + "\n", encoding="utf-8")
    rc, out, err, el = run(["--json", "-C", str(drifted), str(stream)])
    js = jload(out) if out.strip().startswith("{") else {}
    log(f"--- sitbone covering after mid-line {mid} drift ---")
    show(rc, occupy_bits(js) if js else out, err, el)


def section_ws_ignore() -> None:
    banner("10. ignore-space compose vs occupy of covering")
    rc, out, err, el = run(
        [
            "--json",
            "-C",
            str(TREE / "window-origin"),
            str(FIX / "ws-before.jsonl"),
        ]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- trailing-space before, no --ignore-space ---")
    show(rc, occupy_bits(js) if js else out, err, el)
    rc, out, err, el = run(
        [
            "--json",
            "--ignore-space",
            "-C",
            str(TREE / "window-origin"),
            str(FIX / "ws-before.jsonl"),
        ]
    )
    js = jload(out) if out.strip().startswith("{") else {}
    log("--- trailing-space before, --ignore-space ---")
    show(rc, occupy_bits(js) if js else out, err, el)


def main() -> int:
    if ROOT.exists():
        # keep attack.py if we are running from /tmp already
        pass
    FIX.mkdir(parents=True, exist_ok=True)
    TREE.mkdir(parents=True, exist_ok=True)
    log(f"BRAID={BRAID}")
    log(f"VICTIM={VICTIM}")
    log(f"PLEA={PLEA} exists={Path(PLEA).is_file()}")
    log(f"HANK={HANK} exists={Path(HANK).is_file()}")
    log(f"QUIRE={QUIRE} exists={Path(QUIRE).is_file()}")
    log(f"ROOT={ROOT}")
    copy_victim_gold()
    build_fixtures()
    section_selftest()
    section_stack_mid()
    section_window_drift()
    section_nfc()
    section_remarks()
    section_empty_before()
    section_replacement()
    section_inverted_clock()
    section_multifile_subset_emit()
    section_sitbone()
    section_ws_ignore()
    banner("done")
    LOG.write_text("\n".join(transcript) + "\n", encoding="utf-8")
    log(f"wrote {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
