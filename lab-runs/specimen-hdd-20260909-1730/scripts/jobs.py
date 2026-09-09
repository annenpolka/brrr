#!/usr/bin/env python3
"""Throughput / vacancy log for this run. Inference slots must not idle >120s on purpose."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import JOBS_JSONL, RUN_DIR

JST = ZoneInfo("Asia/Tokyo")
MAX_INTENTIONAL_IDLE_S = 120


def now_jst() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z")


def append_job(record: dict) -> None:
    payload = {"at_jst": now_jst(), **record}
    JOBS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with JOBS_JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    rewrite_throughput()


def load_jobs() -> list[dict]:
    if not JOBS_JSONL.exists():
        return []
    rows = []
    for line in JOBS_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def parse_jst(text: str) -> datetime:
    body = text.replace(" JST", "").replace("JST", "").strip()
    return datetime.strptime(body, "%Y-%m-%d %H:%M:%S").replace(tzinfo=JST)


def idle_gaps(rows: list[dict] | None = None) -> list[dict]:
    rows = rows if rows is not None else load_jobs()
    gaps = []
    last_end: datetime | None = None
    for row in rows:
        at = parse_jst(row["at_jst"])
        status = row.get("status") or ""
        if last_end is not None and status in {"started", "taken"}:
            delta = (at - last_end).total_seconds()
            if delta > MAX_INTENTIONAL_IDLE_S and row.get("intentional_idle"):
                gaps.append({"from": last_end.isoformat(), "to": at.isoformat(), "seconds": delta, "job": row.get("job")})
        if status in {"completed", "failed", "blocked", "recorded"}:
            last_end = at
        if status in {"started", "taken"}:
            last_end = at
    return gaps


def rewrite_throughput() -> Path:
    rows = load_jobs()
    lines = [
        "# Throughput",
        "",
        "Vacant inference slots take the next ready job. Clock milestones are deadlines.",
        "R1/test waits register a handle and free the slot. No isomorphic-Dream filler.",
        "",
        f"Updated: {now_jst()}",
        "",
        f"Jobs recorded: {len(rows)}",
        f"Intentional idle gaps >{MAX_INTENTIONAL_IDLE_S}s: {len(idle_gaps(rows))}",
        "",
        "| When JST | Job | Status | Slot | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('at_jst','')} | {row.get('job','')} | {row.get('status','')} | "
            f"{row.get('slot','')} | {row.get('note','')} |"
        )
    lines.append("")
    path = RUN_DIR / "THROUGHPUT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


if __name__ == "__main__":
    rewrite_throughput()
    print(RUN_DIR / "THROUGHPUT.md")
