#!/usr/bin/env python3
"""Canonical scheduler: READY queues, claim/complete, derived boards."""
from __future__ import annotations

import fcntl
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from paths import JOBS_JSONL, QUEUES, RUN_DIR, RUN_ID, SCHEDULER_STATE

JST = ZoneInfo("Asia/Tokyo")

START = datetime(2026, 9, 2, 11, 12, tzinfo=JST)
HARD_END = datetime(2026, 9, 3, 0, 0, tzinfo=JST)
PRESERVATION_START = datetime(2026, 9, 2, 23, 25, tzinfo=JST)
BROAD_FREEZE = datetime(2026, 9, 2, 22, 45, tzinfo=JST)
FIRST_SELECTION_DEADLINE = datetime(2026, 9, 2, 15, 30, tzinfo=JST)
DESTROYER_COVERAGE_DEADLINE = datetime(2026, 9, 2, 17, 0, tzinfo=JST)

# Higher number = claimed first. Ties broken by earlier enqueued_at.
QUEUE_BASE_PRIORITY = {
    "READY_PRESERVE": 100,
    "READY_JUDGE": 90,
    "READY_DESTROY": 80,
    "READY_DOGFOOD": 75,
    "READY_RED_PEN": 72,
    "READY_COUNTEREXAMPLE": 70,
    "READY_HARVEST": 68,
    "READY_GROUND": 65,
    "READY_IMPLEMENT": 62,
    "READY_R1_DREAM": 60,
    "READY_SPECIMEN_CURATE": 55,
    "READY_SPECIMEN_COMPRESS": 50,
    "READY_SPECIMEN_REPRODUCE": 48,
    "READY_SPECIMEN_MUTATE": 45,
    "READY_SPECIMEN_SCOUT": 40,
    "READY_MUTATE": 35,
    "READY_REIMPLEMENT": 34,
    "READY_HYBRID": 33,
}

TARGET_ACTIVE_WORKERS = 14
MIN_ACTIVE_WORKERS = 12
TARGET_R1_IN_FLIGHT = 4
MAX_IDLE_SECONDS = 120


def now_jst(now: datetime | None = None) -> str:
    return (now or datetime.now(JST)).strftime("%Y-%m-%d %H:%M:%S %Z")


def empty_state() -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "start": START.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end": HARD_END.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "preservation_start": PRESERVATION_START.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "broad_freeze": BROAD_FREEZE.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "first_selection_deadline": FIRST_SELECTION_DEADLINE.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "destroyer_coverage_deadline": DESTROYER_COVERAGE_DEADLINE.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "target_active_workers": TARGET_ACTIVE_WORKERS,
        "min_active_workers": MIN_ACTIVE_WORKERS,
        "target_r1_in_flight": TARGET_R1_IN_FLIGHT,
        "max_idle_seconds": MAX_IDLE_SECONDS,
        "mode": "running",
        "prior_art_sealed": True,
        "job_seq": 0,
        "workers": [],
        "machine_tasks": [],
        "ready_jobs": [],
        "lineages": [],
        "specimens": [],
        "r1_budget": {},
        "last_watchdog": None,
        "scheduling_failures": [],
        "events": [],
    }


def _lock_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".lock")


def load_state(path: Path | None = None) -> dict[str, Any]:
    state_path = path or SCHEDULER_STATE
    if not state_path.exists():
        return empty_state()
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], path: Path | None = None) -> None:
    state_path = path or SCHEDULER_STATE
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    tmp.replace(state_path)


def with_state(fn, path: Path | None = None):
    state_path = path or SCHEDULER_STATE
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock = _lock_path(state_path)
    with lock.open("a+", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        state = load_state(state_path)
        result = fn(state)
        save_state(state, state_path)
        return result


def _queue_ok(queue: str) -> None:
    if queue not in QUEUES:
        raise ValueError(f"unknown queue {queue}")


def next_job_id(state: dict[str, Any]) -> str:
    state["job_seq"] = int(state.get("job_seq") or 0) + 1
    return f"job-{state['job_seq']:04d}"


def job_priority(job: dict[str, Any], now: datetime | None = None) -> float:
    now = now or datetime.now(JST)
    base = float(job.get("priority") or QUEUE_BASE_PRIORITY.get(job["queue"], 10))
    if now >= PRESERVATION_START:
        if job["queue"] == "READY_PRESERVE":
            base += 50
        elif job["queue"] not in {"READY_JUDGE", "READY_PRESERVE"}:
            base -= 40
    elif now >= BROAD_FREEZE:
        if job["queue"] in {"READY_R1_DREAM", "READY_SPECIMEN_SCOUT"} and job.get("phase") != "exceptional-jump":
            base -= 30
        if job["queue"] in {"READY_JUDGE", "READY_DESTROY", "READY_DOGFOOD"}:
            base += 15
    return base + float(job.get("priority_boost") or 0)


def enqueue(
    state: dict[str, Any],
    queue: str,
    *,
    input_ref: str,
    expected_output: str,
    kill_condition: str,
    estimated_cost: str = "low",
    priority_reason: str,
    specimen: str | None = None,
    lineage: str | None = None,
    phase: str | None = None,
    job_id: str | None = None,
    extra: dict | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    _queue_ok(queue)
    now = now or datetime.now(JST)
    if now >= HARD_END:
        raise RuntimeError("HARD STOP: no new jobs")
    if state.get("mode") == "hard_stop":
        raise RuntimeError("HARD STOP: scheduler frozen")
    job = {
        "id": job_id or next_job_id(state),
        "queue": queue,
        "status": "READY",
        "specimen": specimen,
        "lineage": lineage,
        "input": input_ref,
        "expected_output": expected_output,
        "kill_condition": kill_condition,
        "estimated_cost": estimated_cost,
        "priority_reason": priority_reason,
        "phase": phase,
        "enqueued_at": now_jst(now),
        "claimed_at": None,
        "completed_at": None,
        "worker": None,
    }
    if extra:
        job.update(extra)
    state.setdefault("ready_jobs", []).append(job)
    _append_event(state, "enqueue", job["id"], queue)
    return job


def ready_jobs(state: dict[str, Any]) -> list[dict[str, Any]]:
    return [j for j in state.get("ready_jobs") or [] if j.get("status") == "READY"]


def claim(
    state: dict[str, Any],
    worker: str,
    *,
    now: datetime | None = None,
    queues: list[str] | None = None,
) -> dict[str, Any] | None:
    now = now or datetime.now(JST)
    if now >= HARD_END or state.get("mode") == "hard_stop":
        return None
    if state.get("mode") == "preservation" and now >= PRESERVATION_START:
        allowed = {"READY_PRESERVE", "READY_JUDGE"}
        queues = list(allowed if queues is None else set(queues) & allowed)
    candidates = ready_jobs(state)
    if queues:
        candidates = [j for j in candidates if j["queue"] in queues]
    if not candidates:
        return None
    candidates.sort(key=lambda j: (-job_priority(j, now), j.get("enqueued_at") or "", j["id"]))
    job = candidates[0]
    job["status"] = "CLAIMED"
    job["claimed_at"] = now_jst(now)
    job["worker"] = worker
    workers = state.setdefault("workers", [])
    rec = next((w for w in workers if w.get("id") == worker), None)
    if rec is None:
        rec = {"id": worker, "status": "active", "job": job["id"]}
        workers.append(rec)
    else:
        rec["status"] = "active"
        rec["job"] = job["id"]
    _append_event(state, "claim", job["id"], job["queue"], worker=worker)
    return job


def complete(
    state: dict[str, Any],
    job_id: str,
    *,
    result: str = "ok",
    artifact: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(JST)
    job = _find(state, job_id)
    job["status"] = "DONE" if result == "ok" else result.upper()
    job["completed_at"] = now_jst(now)
    if artifact:
        job["artifact"] = artifact
    worker_id = job.get("worker")
    for w in state.get("workers") or []:
        if w.get("id") == worker_id:
            w["status"] = "vacant"
            w["job"] = None
    _append_event(state, "complete", job_id, job["queue"], result=result)
    _append_job_log(job)
    return job


def _find(state: dict[str, Any], job_id: str) -> dict[str, Any]:
    for job in state.get("ready_jobs") or []:
        if job["id"] == job_id:
            return job
    raise KeyError(job_id)


def _append_event(state: dict[str, Any], kind: str, job_id: str, queue: str, **extra: Any) -> None:
    events = state.setdefault("events", [])
    events.append(
        {"at": now_jst(), "kind": kind, "job": job_id, "queue": queue, **extra}
    )
    if len(events) > 500:
        del events[: len(events) - 500]


def _append_job_log(job: dict[str, Any]) -> None:
    JOBS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with JOBS_JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(job, ensure_ascii=False) + "\n")


def queue_depths(state: dict[str, Any]) -> dict[str, int]:
    depths = {q: 0 for q in QUEUES}
    for job in ready_jobs(state):
        depths[job["queue"]] = depths.get(job["queue"], 0) + 1
    return depths


def backlog_floor(free_slots: int) -> int:
    return max(TARGET_ACTIVE_WORKERS, 2 * max(free_slots, 0))


def set_mode(state: dict[str, Any], mode: str, now: datetime | None = None) -> None:
    allowed = {"running", "preservation", "hard_stop"}
    if mode not in allowed:
        raise ValueError(mode)
    now = now or datetime.now(JST)
    if mode == "preservation" and now < PRESERVATION_START:
        # Clock may be early only if operator forces it after 23:25 check elsewhere.
        pass
    state["mode"] = mode
    _append_event(state, "mode", "-", "-", mode=mode)


def render_status(state: dict[str, Any], now: datetime | None = None) -> str:
    now = now or datetime.now(JST)
    depths = queue_depths(state)
    ready = sum(depths.values())
    active = [w for w in state.get("workers") or [] if w.get("status") == "active"]
    vacant = [w for w in state.get("workers") or [] if w.get("status") == "vacant"]
    lines = [
        f"# STATUS {state.get('run_id')}",
        "",
        f"Clock: {now_jst(now)}",
        f"Mode: **{state.get('mode')}**",
        f"Prior art sealed: {state.get('prior_art_sealed')}",
        f"Active workers: {len(active)} / target {state.get('target_active_workers')}",
        f"Vacant: {len(vacant)}",
        f"Ready jobs: {ready} (floor {backlog_floor(max(0, TARGET_ACTIVE_WORKERS - len(active)))})",
        f"R1 in flight: {len([t for t in state.get('machine_tasks') or [] if t.get('kind') == 'r1' and t.get('status') == 'running'])}",
        "",
        "## Ready queues",
        "",
        "| Queue | Depth |",
        "| --- | ---: |",
    ]
    for q in QUEUES:
        lines.append(f"| {q} | {depths[q]} |")
    lines += ["", "## Active workers", ""]
    if not active:
        lines.append("(none)")
    else:
        for w in active:
            lines.append(f"- `{w['id']}` job={w.get('job')}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    def _status(state):
        sys.stdout.write(render_status(state))
        (RUN_DIR / "STATUS.md").write_text(render_status(state), encoding="utf-8")
        return state

    if cmd == "init":
        if SCHEDULER_STATE.exists():
            print(f"exists {SCHEDULER_STATE}")
            return
        save_state(empty_state())
        print(SCHEDULER_STATE)
        return
    if cmd == "status":
        with_state(_status)
        return
    if cmd == "enqueue":
        # scheduler.py enqueue QUEUE --input ... --expected ... --kill ... --reason ...
        queue = sys.argv[2]
        args = dict(zip(sys.argv[3::2], sys.argv[4::2]))

        def _enq(state):
            job = enqueue(
                state,
                queue,
                input_ref=args.get("--input", ""),
                expected_output=args.get("--expected", ""),
                kill_condition=args.get("--kill", "20m no artifact"),
                estimated_cost=args.get("--cost", "low"),
                priority_reason=args.get("--reason", "manual"),
                specimen=args.get("--specimen"),
                lineage=args.get("--lineage"),
                phase=args.get("--phase"),
            )
            print(json.dumps(job, indent=2))
            return job

        with_state(_enq)
        return
    if cmd == "claim":
        worker = sys.argv[2] if len(sys.argv) > 2 else "coordinator"

        def _claim(state):
            job = claim(state, worker)
            print(json.dumps(job, indent=2) if job else "null")
            return job

        with_state(_claim)
        return
    if cmd == "complete":
        job_id = sys.argv[2]
        result = sys.argv[3] if len(sys.argv) > 3 else "ok"

        def _done(state):
            job = complete(state, job_id, result=result)
            print(json.dumps({"id": job["id"], "status": job["status"]}, indent=2))
            return job

        with_state(_done)
        return
    if cmd == "mode":
        mode = sys.argv[2]

        def _mode(state):
            set_mode(state, mode)
            print(mode)
            return mode

        with_state(_mode)
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
