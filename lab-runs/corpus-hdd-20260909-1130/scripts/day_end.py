#!/usr/bin/env python3
"""Save / drain / HARD_STOP for this run only. Never kill 9/2 PIDs."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from credits import fetch_credits, public_snapshot
from hash_bundle import hash_tree
from clock_gate import GATES, ORIGINAL_HARD_END
from paths import CORPUS_ROOT, HDD_ROOT, REPO_ROOT, RUN_DIR, RUN_ID, SNAPSHOT_ID
from r1_budget import conservative_spend, load_ledger, remaining_usd, reported_spend, rewrite_budget_md

JST = ZoneInfo("Asia/Tokyo")
HARD_END = GATES["hard_stop"]
RECEIPT = REPO_ROOT / "docs/preparation/evidence-pilot-receipt.json"
SCRATCH = Path(os.environ.get("GOAL_SCRATCH", "")).resolve() if os.environ.get("GOAL_SCRATCH") else None


def now() -> datetime:
    return datetime.now(JST)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def this_run_pids() -> list[dict]:
    """Only this run's Dreamer/hdd.py/dream.sh workers. Never 9/2 PIDs or the coordinator."""
    out = subprocess.run(["ps", "-ax", "-o", "pid=,command="], capture_output=True, text=True, check=True)
    hits = []
    markers = (
        str(HDD_ROOT),
        f"{RUN_ID}/scripts/dream.sh",
        f"hdd.py --root {HDD_ROOT}",
    )
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_s, _, cmd = line.partition(" ")
        if "specimen-hdd-20260902" in cmd or "lab-hdd/" in cmd:
            continue
        if any(m in cmd for m in markers) and ("hdd.py" in cmd or "dream.sh" in cmd):
            hits.append({"pid": int(pid_s), "command": cmd})
    return hits


def cmd(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=REPO_ROOT, check=True, text=True, capture_output=True)


def require_gate(name: str, at: datetime) -> None:
    if at < GATES[name]:
        raise SystemExit(f"{name} refused before {GATES[name].isoformat()}; now={at.isoformat()}")


def save(at: datetime | None = None) -> None:
    at = at or now()
    require_gate("save", at)
    credits = public_snapshot(fetch_credits())
    write(RUN_DIR / "credits-end.json", json.dumps(credits, indent=2) + "\n")
    rewrite_budget_md()
    ledger = load_ledger()
    export_dir = CORPUS_ROOT / "exports" / "reported-discovery-v1-day-end"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    exported = cmd(
        [
            sys.executable,
            "scripts/corpus.py",
            "--root",
            str(CORPUS_ROOT),
            "export",
            SNAPSHOT_ID,
            "--output",
            str(export_dir),
        ]
    )
    write(RUN_DIR / "export-day-end.log", exported.stdout + exported.stderr)
    hashes = hash_tree(export_dir)
    expected = json.loads(RECEIPT.read_text(encoding="utf-8"))["export"]["files"]
    if hashes != expected:
        raise SystemExit(f"day-end export hash mismatch: {hashes} vs {expected}")
    bk = REPO_ROOT / ".brrr-corpus-backups" / "mini-followup-20260909-hdd-day-end"
    rst = REPO_ROOT / ".brrr-corpus-restored" / "mini-followup-20260909-hdd-day-end"
    if bk.exists():
        shutil.rmtree(bk)
    if rst.exists():
        shutil.rmtree(rst)
    cmd([sys.executable, "scripts/corpus.py", "--root", str(CORPUS_ROOT), "backup", "--output", str(bk)])
    cmd([sys.executable, "scripts/corpus.py", "restore", "--backup", str(bk), "--output", str(rst)])
    rst_export = rst / "exports" / "reported-discovery-v1"
    cmd(
        [
            sys.executable,
            "scripts/corpus.py",
            "--root",
            str(rst),
            "export",
            SNAPSHOT_ID,
            "--output",
            str(rst_export),
        ]
    )
    restored = hash_tree(rst_export)
    write(
        RUN_DIR / "restore-hashes-day-end.txt",
        json.dumps({"expected": expected, "restored": restored, "identical": restored == expected}, indent=2) + "\n",
    )
    if restored != expected:
        raise SystemExit("day-end restore hashes drifted")
    write(
        RUN_DIR / "RERUN.md",
        f"""# 再実行方法

cwd: repository root `{REPO_ROOT}`

1. Do not start before 11:30 JST on a new day without a new run id.
2. Export the same snapshot:

       python3 scripts/corpus.py --root .brrr-corpus/mini-followup export {SNAPSHOT_ID} --output .brrr-corpus/mini-followup/exports/reported-discovery-v1

3. Copy only the public 6 files. Do not pass collector root, PRIVATE reviews, past runs, or the execplan to the Dreamer.
4. HDD:

       python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/{RUN_ID} status --trial case-001-a

   Resume with `status`, not `init`, for the same trial.
5. Dreamer remains `deepseek/deepseek-r1`. No silent substitute.
6. Candidate tool:

       python3 scripts/runpair.py --cwd DIR -- deno run a.js
""",
    )
    write(
        RUN_DIR / "TOMORROW.md",
        """# Tomorrow Test (0–2)

1. **runpair** — try on one other command that writes a sidecar the second invocation then trips over (not issue 32113 as 未知holdout; that case is discovery). If no second independent PASS input exists, treat transfer as unverified.

0 other tools. Empty is allowed.
""",
    )
    write(
        RUN_DIR / "FINAL_JURY.md",
        f"""# Final jury

Host only. Not human.

- Smallness: runpair is one command, JSON file-delta, no lockfile parser.
- Usefulness: binds first-run sidecar appearance to second-run rc on the 32113 public files (実機).
- Novelty: USEFUL_COMPOSITION, not NOVEL_AFFORDANCE.
- Skeptical 反証: true/false/writer/symlink/nested; FIFO/symlink limits documented.
- 実機: Deno 2.8.1 (not 2.6.8) still showed deno.lock then `@.` error.

Tomorrow: runpair only, or 0 if the user does not want a composition.

Observed spend ${reported_spend(ledger):.6f}; conservative ${conservative_spend(ledger):.6f}; remaining ${remaining_usd(ledger):.6f}.
""",
    )
    write(
        RUN_DIR / "EVOLUTION_REPORT.md",
        f"""# Evolution report (this run only)

Run `{RUN_ID}` started 2026-09-09 11:30:22 JST, hard end 2026-09-10 00:00 JST not extended.

- Snapshot `{SNAPSHOT_ID}` → 6 public hashes → trial `case-001-a` → 3 R1 Dreams → 3 host Red Pens.
- R1 HTTP success was design material. Turns 1–3 fabricated Deno/cli observations. Harvested twice-run directory delta as runpair.
- Inputs: 1 discovery case, 小規模試行, not 未知holdout. 35901 HOLD.
- Cost: observed ${reported_spend(ledger):.6f}, conservative ${conservative_spend(ledger):.6f}, cap ${ledger['effective_cap_usd']:.4f}, calls {ledger.get('total_calls', 0)}.
- Coordinator main was not given candidate product.
""",
    )
    write(
        RUN_DIR / "採否.md",
        """# 採否理由

KEEP: runpair (USEFUL_COMPOSITION). 実機で first `deno run a.js` が `deno.lock` を作り、second が `@.` で落ちる。既存の `cmd; ls; cmd` はその結び付きを一つの契約にしない。

KILL: fictional unfamiliar-cli / verify-lock. Dream 出力は transcript の複製であり、この環境のプロセス出力ではない。

HOLD (not PASS): issue 35901. 生成 lockfile / node_modules / DENO_DIR が無い。件数合わせで PASS にしない。

成果物最低数は置かない。Tomorrow は runpair 1件、または 0 件も可。
""",
    )
    if SCRATCH:
        shutil.copy(RUN_DIR / "credits-end.json", SCRATCH / "credits-end.json")
        shutil.copy(RUN_DIR / "restore-hashes-day-end.txt", SCRATCH / "restore-hashes.txt")
        shutil.copy(RUN_DIR / "採否.md", SCRATCH / "採否.md")
        shutil.copy(RUN_DIR / "RERUN.md", SCRATCH / "RERUN.md")
    print("save complete")


def drain(at: datetime | None = None) -> None:
    at = at or now()
    require_gate("drain", at)
    pids = this_run_pids()
    write(RUN_DIR / "drain-ps.json", json.dumps({"at_jst": now().strftime("%Y-%m-%d %H:%M:%S %Z"), "pids": pids}, indent=2) + "\n")
    for proc in pids:
        cmd_l = proc["command"]
        if "day_end.py" in cmd_l or "clock_gate.py" in cmd_l:
            continue
        try:
            os.kill(proc["pid"], 15)
        except ProcessLookupError:
            pass
    print("drain signalled", pids)


def hard_stop(at: datetime | None = None) -> None:
    at = at or now()
    require_gate("hard_stop", at)
    pids = this_run_pids()
    live = [
        p
        for p in pids
        if "day_end.py" not in p["command"] and "clock_gate.py" not in p["command"]
    ]
    write(
        RUN_DIR / "HARD_STOP.md",
        f"""HARD STOP at {at.strftime("%Y-%m-%d %H:%M:%S %Z")}
Run: {RUN_ID}
Matched dirs: {RUN_DIR}, {HDD_ROOT}
Live processes for this run (excluding this stopper): {len(live)}
{json.dumps(live, indent=2)}
Old 9/2 PIDs were not killed.
""",
    )
    ps_text = subprocess.run(["ps", "-ax", "-o", "pid=,command="], capture_output=True, text=True, check=True).stdout
    write(RUN_DIR / "hard-stop-ps.txt", ps_text)
    write(
        RUN_DIR / "clock-stop.txt",
        "\n".join(
            [
                "phase: hard_stop",
                f"captured_at_jst: {at.isoformat()}",
                f"human: {at.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                f"hard_end: {GATES['hard_stop'].isoformat()}",
                f"original_hard_end: {ORIGINAL_HARD_END.isoformat()}",
                "hard_end_extended: no",
                f"this_run_live_pids: {len(live)}",
                f"run_id: {RUN_ID}",
            ]
        )
        + "\n",
    )
    if live:
        raise SystemExit(f"this run still has live processes: {live}")
    print("HARD_STOP recorded; live=0")


def copy_scratch() -> None:
    if not SCRATCH:
        return
    for name in (
        "credits-end.json",
        "restore-hashes-day-end.txt",
        "HARD_STOP.md",
        "hard-stop-ps.txt",
        "R1_BUDGET.md",
        "TOMORROW.md",
        "FINAL_JURY.md",
        "EVOLUTION_REPORT.md",
        "RERUN.md",
        "clock-stop.txt",
        "採否.md",
        "restore-hashes.txt",
    ):
        src = RUN_DIR / name
        if src.exists():
            shutil.copy(src, SCRATCH / name)


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "save":
        save()
    elif action == "drain":
        drain()
    elif action == "hard-stop":
        hard_stop()
        copy_scratch()
    else:
        raise SystemExit("usage: day_end.py save|drain|hard-stop")


if __name__ == "__main__":
    main()
