#!/usr/bin/env python3
"""Sync scheduler after wave-2 completions, harvests, and envlayers embodiment."""
from __future__ import annotations

from scheduler import claim, complete, enqueue, with_state


def _complete_if_claimed(state, job_id: str, artifact: str) -> None:
    job = next(j for j in state["ready_jobs"] if j["id"] == job_id)
    if job["status"] == "CLAIMED":
        complete(state, job_id, artifact=artifact)
    elif job["status"] == "READY":
        claim(state, "coordinator-tick")
        # claim() takes highest READY; only complete if we got this id
        got = next(j for j in state["ready_jobs"] if j["id"] == job_id)
        if got.get("worker") == "coordinator-tick" and got["status"] == "CLAIMED":
            complete(state, job_id, artifact=artifact)


def _force_claim_complete(state, job_id: str, worker: str, artifact: str) -> None:
    job = next(j for j in state["ready_jobs"] if j["id"] == job_id)
    if job["status"] == "DONE":
        return
    job["status"] = "CLAIMED"
    job["worker"] = worker
    job["claimed_at"] = job.get("claimed_at") or job.get("enqueued_at")
    complete(state, job_id, artifact=artifact)


def main() -> None:
    def fn(state):
        # First-turn R1 jobs that already produced dreamer.md
        done_first = {
            "job-0011": "hdd-walrus/iterations/0001-dreamer.md",
            "job-0012": "hdd-fingerprint/iterations/0001-dreamer.md",
            "job-0013": "hdd-silent-add/iterations/0001-dreamer.md",
            "job-0014": "hdd-env-empty/iterations/0001-dreamer.md",
            "job-0015": "hdd-order/iterations/0001-dreamer.md",
            "job-0016": "hdd-npm-peers/iterations/0001-dreamer.md",
            "job-0017": "hdd-identity/iterations/0001-dreamer.md",
            "job-0018": "hdd-rootdir/iterations/0001-dreamer.md",
        }
        for jid, art in done_first.items():
            job = next(j for j in state["ready_jobs"] if j["id"] == jid)
            if job["status"] != "DONE":
                if job["status"] != "CLAIMED":
                    job["status"] = "CLAIMED"
                    job["worker"] = job.get("worker") or "coordinator-tick"
                complete(state, jid, artifact=art)

        # Follow-up / wave-3 R1 actually in flight (launched ~11:43 without claim)
        inflight = {
            "job-0025": ("r1-walrus-fu", "hdd-walrus"),
            "job-0026": ("r1-fingerprint-fu", "hdd-fingerprint"),
            "job-0027": ("r1-silent-add-fu", "hdd-silent-add"),
            "job-0028": ("r1-rerun", "hdd-rerun"),
        }
        for jid, (worker, trial) in inflight.items():
            job = next(j for j in state["ready_jobs"] if j["id"] == jid)
            if job["status"] == "READY":
                job["status"] = "CLAIMED"
                job["worker"] = worker
                job["claimed_at"] = "2026-09-02 11:43:00 JST"
                rec = next((w for w in state["workers"] if w["id"] == worker), None)
                if rec is None:
                    state["workers"].append({"id": worker, "status": "active", "job": jid})
                else:
                    rec["status"] = "active"
                    rec["job"] = jid

        # Scout race-test filled by specimen-053
        job22 = next(j for j in state["ready_jobs"] if j["id"] == "job-0022")
        if job22["status"] == "READY":
            job22["status"] = "CLAIMED"
            job22["worker"] = "scout-race"
            job22["claimed_at"] = "2026-09-02 11:46:00 JST"
        if job22["status"] == "CLAIMED":
            complete(state, "job-0022", artifact="specimens/specimen-053")

        # Harvests already written
        for queue, input_ref, expected, reason, specimen, lineage, artifact, worker in [
            (
                "READY_HARVEST",
                "hdd-env-empty redpen HARVEST_NOW",
                "hdd-origins/hdd-env-empty.md",
                "layer empty-vs-unset",
                "specimen-010",
                "envlayers",
                "hdd-origins/hdd-env-empty.md",
                "harvest-envlayers",
            ),
            (
                "READY_HARVEST",
                "hdd-order redpen HARVEST_NOW",
                "hdd-origins/hdd-order.md",
                "leak plus exposing order",
                "specimen-009",
                "leakorder",
                "hdd-origins/hdd-order.md",
                "harvest-leakorder",
            ),
            (
                "READY_HARVEST",
                "hdd-identity redpen HARVEST_NOW",
                "hdd-origins/hdd-identity.md",
                "stale-import bind identity",
                "specimen-013",
                "bindname",
                "hdd-origins/hdd-identity.md",
                "harvest-bindname",
            ),
        ]:
            exists = any(
                j.get("input") == input_ref and j["queue"] == queue for j in state["ready_jobs"]
            )
            if not exists:
                job = enqueue(
                    state,
                    queue,
                    input_ref=input_ref,
                    expected_output=expected,
                    kill_condition="20m",
                    estimated_cost="low",
                    priority_reason=reason,
                    specimen=specimen,
                    lineage=lineage,
                )
                job["status"] = "CLAIMED"
                job["worker"] = worker
                complete(state, job["id"], artifact=artifact)

        ground_exists = any(
            j.get("lineage") == "envlayers" and j["queue"] == "READY_GROUND"
            for j in state["ready_jobs"]
        )
        if not ground_exists:
            job = enqueue(
                state,
                "READY_GROUND",
                input_ref="hdd-origins/hdd-env-empty.md",
                expected_output="worktree envlayers CLI",
                kill_condition="40m",
                estimated_cost="low",
                priority_reason="first embodiment",
                specimen="specimen-010",
                lineage="envlayers",
            )
            job["status"] = "CLAIMED"
            job["worker"] = "grounder-envlayers"
            complete(
                state,
                job["id"],
                artifact="~/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers",
            )

        dog_exists = any(
            j.get("lineage") == "envlayers" and j["queue"] == "READY_DOGFOOD"
            for j in state["ready_jobs"]
        )
        if not dog_exists:
            job = enqueue(
                state,
                "READY_DOGFOOD",
                input_ref="envlayers CLI specimen-010 + unseen-absent",
                expected_output="scratch/demos/demo-envlayers-*.log",
                kill_condition="20m",
                estimated_cost="low",
                priority_reason="original x2 + unseen",
                specimen="specimen-010",
                lineage="envlayers",
            )
            job["status"] = "CLAIMED"
            job["worker"] = "dogfood-envlayers"
            complete(state, job["id"], artifact="scratch/demos/demo-envlayers-1.log")

        if not any(j.get("trial") == "hdd-race" for j in state["ready_jobs"]):
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref="seeds/specimen-053.md trial=hdd-race",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="race-test parallel git.store",
                specimen="specimen-053",
                lineage="hdd-race",
                phase="cambrian",
                extra={"trial": "hdd-race"},
            )

        if not any(
            j.get("lineage") == "hdd-npm-peers" and j.get("phase") == "follow-up" and j["status"] == "READY"
            for j in state["ready_jobs"]
        ):
            enqueue(
                state,
                "READY_R1_DREAM",
                input_ref="follow-up hdd-npm-peers text pressure no network",
                expected_output="0002-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason="text pressure unused fetches",
                specimen="specimen-004",
                lineage="hdd-npm-peers",
                phase="follow-up",
                extra={"trial": "hdd-npm-peers", "turn": 2},
            )

        if not any(
            j.get("lineage") == "hdd-rootdir" and j["queue"] == "READY_COUNTEREXAMPLE"
            for j in state["ready_jobs"]
        ):
            enqueue(
                state,
                "READY_COUNTEREXAMPLE",
                input_ref="hdd-rootdir owned two-directory layout",
                expected_output="derived fixture packet",
                kill_condition="25m",
                estimated_cost="low",
                priority_reason="rootdir counterexample fixture",
                specimen="specimen-002",
                lineage="hdd-rootdir",
            )

        if not any(
            j.get("lineage") == "envlayers" and j["queue"] == "READY_DESTROY"
            for j in state["ready_jobs"]
        ):
            enqueue(
                state,
                "READY_DESTROY",
                input_ref="envlayers runnable CLI",
                expected_output="destroyers/DESTROYER_envlayers.md",
                kill_condition="25m",
                estimated_cost="low",
                priority_reason="first runnable candidate",
                specimen="specimen-010",
                lineage="envlayers",
            )

        if not any(
            j.get("lineage") == "leakorder" and j["queue"] == "READY_GROUND"
            for j in state["ready_jobs"]
        ):
            enqueue(
                state,
                "READY_GROUND",
                input_ref="hdd-origins/hdd-order.md",
                expected_output="worktree leakorder CLI",
                kill_condition="40m",
                estimated_cost="low",
                priority_reason="second harvest embodiment",
                specimen="specimen-009",
                lineage="leakorder",
            )
        if not any(
            j.get("lineage") == "bindname" and j["queue"] == "READY_GROUND"
            for j in state["ready_jobs"]
        ):
            enqueue(
                state,
                "READY_GROUND",
                input_ref="hdd-origins/hdd-identity.md",
                expected_output="worktree bindname CLI",
                kill_condition="40m",
                estimated_cost="low",
                priority_reason="third harvest embodiment",
                specimen="specimen-013",
                lineage="bindname",
            )

        for t in state.get("machine_tasks") or []:
            if t.get("trial") in {"hdd-order", "hdd-npm-peers", "hdd-identity", "hdd-rootdir"}:
                t["status"] = "done"
        existing = {(t.get("trial"), t.get("id")) for t in state.get("machine_tasks") or []}
        for tid, worker, trial in [
            ("r1-hdd-walrus-fu", "r1-walrus-fu", "hdd-walrus"),
            ("r1-hdd-fingerprint-fu", "r1-fingerprint-fu", "hdd-fingerprint"),
            ("r1-hdd-silent-add-fu", "r1-silent-add-fu", "hdd-silent-add"),
            ("r1-hdd-rerun", "r1-rerun", "hdd-rerun"),
        ]:
            if not any(t.get("id") == tid for t in state.get("machine_tasks") or []):
                state.setdefault("machine_tasks", []).append(
                    {"id": tid, "kind": "r1", "status": "running", "worker": worker, "trial": trial}
                )

        if not any(s.get("id") == "specimen-053" for s in state.get("specimens") or []):
            state.setdefault("specimens", []).append({"id": "specimen-053"})

        print("job_seq", state.get("job_seq"))
        return state

    with_state(fn)


if __name__ == "__main__":
    main()
