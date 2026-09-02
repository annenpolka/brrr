#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 149+.

Packed (unique vs 001-148; 075 not overwritten; not bazel#29298):
1) compose-spec/compose-go#654 / docker/compose#11962:
   leftover image ENV default after listed `FOO` (no equals) was dropped
   from the service environment map. Listed-without-equals, empty `FOO=`,
   omitted, and unset-in-container are different identities.
2) systemd/systemd#43355:
   leftover cwd search-path identity from empty `::` components in
   SYSTEMD_UNIT_PATH. Unset, empty `""`, trailing `:`, and `::` cwd are
   different identities.

SKIP claimed jobs 0634-0636 (no unique leftover-identity pair this tick).
Do not pack leftover-flag omitted-flush/cache-line TSV (ansflush/skafdig
class). Distinct from already packed 001-148. 112 SKIP dup 110; 113 KILL
dup 111 class. Never overwrite 075.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SEEDS, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 149
WORKER = "scout-leftover-2119"
SKIP_JOBS = {
    "job-0634": (
        "skip conan leftover package cache vs recipe identity: #18954/"
        "#20175/#17134 still OPEN; #19740 MERGED is alias removal not leftover "
        "package_id vs recipe revision; #20057 closed without PR. not inventing "
        "refs; not 136"
    ),
    "job-0635": (
        "skip nomad leftover artifact vs job identity: #27398 MERGED is "
        "Windows ReadDir invalid-argument not leftover-identity; #28150 leftover "
        "download skip still OPEN; #5217 OPEN optional cache; #23799 closed "
        "not_planned no PR. not inventing refs; not 118"
    ),
    "job-0636": (
        "skip dagger leftover cache vs env identity: #12902 MERGED is FEATURE "
        "withVolatileVariable (intentional cache exclusion, not leftover after "
        "env should invalidate); #12883 OPEN URI secrets on cache hits; #13285 "
        "leftover version cache is omitted version from CliDev (leftover-flag "
        "omitted-key TSV). not inventing refs; not 075"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: zeitwerk leftover same-name const vs moved file identity not 110/111",
        "unique zeitwerk leftover helper vs moved definition if pinned",
    ),
    (
        "public OSS: python-dotenv leftover empty vs unset if #684 merges not 010/031/149",
        "unique dotenv leftover empty-vs-unset if pinned",
    ),
    (
        "public OSS: leftover same-name helper vs moved definition not bindname/075",
        "unique leftover helper vs moved definition if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 180):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_compose(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: compose-spec/compose-go
failing_ref: 65600cee45d45771a1faa6ddaf87b23ca4d2400c
fixed_ref: 6adefd584b8088e0c6817bf54f5715595dd41301
source_issue: https://github.com/docker/compose/issues/11962
source_pr: https://github.com/compose-spec/compose-go/pull/654
mechanism_tags:
  - leftover-empty-vs-unset
  - listed-without-equals-dropped
  - leftover-image-env-default
ecosystem: compose
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Compose-go `Normalize` can keep the identity of a **previous image ENV default** after the compose file listed `FOO` (no equals, no value) and that listing should have meant unset-in-container. `resolve` drops a listed-without-equals name when the user environment has no matching entry. The service environment map then omits `FOO`. The leftover identity is the image `ENV FOO=not_empty` default, not unset.

On failing_ref `65600cee45d45771a1faa6ddaf87b23ca4d2400c`:

```
func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
    case []any:
        var resolved []any
        for _, val := range v {
            if r, ok := resolve(val, fn); ok {
                resolved = append(resolved, r)
            }
        }
        return resolved, true
    case map[string]any:
        resolved := map[string]any{}
        for key, val := range v {
            if val != nil {
                resolved[key] = val
                continue
            }
            if s, ok := fn(key); ok {
                resolved[key] = s
            }
        }
        return resolved, true
    case string:
        if !strings.Contains(v, "=") {
            if val, ok := fn(v); ok {
                return fmt.Sprintf("%s=%s", v, val), true
            }
            return "", false
        }
        return v, true
    default:
        return v, false
    }
}
```

`service["environment"]` and `build["args"]` both call the same `resolve`. Listed-without-equals `FOO` with no user-env match returns `("", false)` and is dropped. `FOO=` (equals, empty) is a different identity and is kept. Image `ENV EMPTY=not_empty` then supplies leftover `not_empty`.

Public report (docker/compose#11962). Image `ENV EMPTY=not_empty`; compose lists `- EMPTY`; `echo "=$EMPTY="` prints `=not_empty=` (leftover image default) instead of `==` (unset). `FOO=` empty string is `==` with empty. User-env `EMPTY=hello` is `=hello=`.

In-tree after the repair (not on failing_ref): `resolve(a, fn, keepEmpty bool)`; environment uses `keepEmpty=true` and keeps listed-without-equals as `nil` / the bare name. Build args stay `keepEmpty=false`.

Case A — listed `FOO`, user env has `FOO=bar`:
  current resolved identity `FOO=bar`
  not leftover-after-drop

Case B — listed `FOO` (no equals), user env has no `FOO`, leftover drop:
  leftover: previous image ENV default / omitted from service environment
  listed-without-equals dropped (`"", false`)
  container still has image default

Case C — listed `FOO=` (equals, empty string):
  empty-string identity
  not unset; not leftover image default

Case D — environment keepEmpty (post-repair shape, not on failing_ref):
  listed-without-equals kept as nil / bare name
  container unsets; not leftover image default

The developer wants to know which identity case B actually used for `FOO` after the listing: leftover previous-image default (listed-without-equals dropped), current unset, empty string, or omitted (no env map).
""",
        observed="""# OBSERVED

Public docker/compose#11962 (closed 2024-07-10). compose-spec/compose-go PR 654 squash `6adefd584b8088e0c6817bf54f5715595dd41301` (parent `65600cee45d45771a1faa6ddaf87b23ca4d2400c`). docker/compose PR 11965 bumps compose-go and adds e2e `TestUnsetEnv`. Local compose-go was not performed on this lab host.

Issue body: image `ENV VAR "default"`; compose `environment: - VAR` (no value). Before v2.24.7 the variable was unset from the container. After, leftover image default stayed. `VAR=` (equals, empty) is empty in the container on both sides.

On failing_ref, `Normalize` calls `resolve` for environment and build args with one signature. Listed-without-equals and no user-env match is dropped. Build args are supposed to keep Dockerfile defaults; environment listed-without-equals is supposed to unset.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global proxy. specimen-079 helm null vs omitempty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 65600cee45d45771a1faa6ddaf87b23ca4d2400c
# loader/normalize.go resolve / service["environment"]

# public shape:
# leftover image ENV default after listed-without-equals dropped
# FOO= empty string is a different identity
# user-env match yields current FOO=value
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""compose-spec/compose-go
  loader/normalize.go
  loader/normalize_test.go
""",
        source="""repository: compose-spec/compose-go
issue: https://github.com/docker/compose/issues/11962
pr: https://github.com/compose-spec/compose-go/pull/654
compose_pr: https://github.com/docker/compose/pull/11965
failing_ref (parent of squash on main): 65600cee45d45771a1faa6ddaf87b23ca4d2400c
fixed_ref (keepEmpty on environment resolve): 6adefd584b8088e0c6817bf54f5715595dd41301
merged_at: 2024-07-08T10:13:40Z
pr_author: ndeloof
merged_by: ndeloof
changed_files: loader/normalize.go, loader/normalize_test.go
pr_title: keep empty environment variables as those must be UNSET in container
scout_note: not 010 local env-empty / not 031 pip empty-override. leftover image ENV default after listed-without-equals dropped. unique vs 001-148.
""",
        answer_key="""KNOWN FIX (sealed): compose-spec/compose-go PR 654 squash 6adefd584b8088e0c6817bf54f5715595dd41301.

failing_ref is parent 65600cee45d45771a1faa6ddaf87b23ca4d2400c.

resolve dropped listed-without-equals names when user env had no match. Environment listing `FOO` then omitted FOO from the service map. Leftover identity was the image ENV default.

PR repair: resolve(a, fn, keepEmpty bool); environment keepEmpty=true keeps listed-without-equals as nil / bare name so the container unsets. Build args stay keepEmpty=false.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (user-env match vs leftover image default after drop vs FOO= empty vs keepEmpty unset)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — listed-without-equals, empty string, omitted, and unset-in-container are different identities; leftover image default stayed current
ecosystem: compose / environment resolve
mechanism_family: leftover-empty-vs-unset, listed-without-equals-dropped, leftover-image-env-default

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "resolve_failing.go": """// Reduced excerpt of resolve on failing_ref
// loader/normalize.go
// 65600cee45d45771a1faa6ddaf87b23ca4d2400c
// listed-without-equals with no user-env match returns "", false and is dropped.
// leftover identity is the image ENV default.

func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
    case string:
        if !strings.Contains(v, "=") {
            if val, ok := fn(v); ok {
                return fmt.Sprintf("%s=%s", v, val), true
            }
            return "", false
        }
        return v, true
    default:
        return v, false
    }
}

// service["environment"] and build["args"] share this resolve
""",
            "leftover_identity_split.txt": """Registry / fixture:
  compose-go Normalize environment resolve
  leftover image ENV default after listed-without-equals dropped

Case A (listed FOO, user env FOO=bar):
  current resolved identity
  not leftover-after-drop

Case B (listed FOO, no user env, leftover drop):
  leftover: previous image ENV default
  listed-without-equals omitted from service environment
  container still has image default

Case C (listed FOO= empty string):
  empty-string identity
  not unset; not leftover image default

Case D (environment keepEmpty):
  listed-without-equals kept as nil / bare name
  container unsets
  not leftover image default

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  helm null vs omitempty (specimen-079)
""",
        },
    )


def packet_systemd(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: systemd/systemd
failing_ref: cad2c455ec1acff29a81421c58adbe0ffc191f65
fixed_ref: f4284e9cebac67ad7af3bc27b736cf1107b88127
source_issue: https://github.com/systemd/systemd/pull/43355
source_pr: https://github.com/systemd/systemd/pull/43355
mechanism_tags:
  - leftover-empty-vs-unset
  - empty-path-component-as-cwd
  - search-path-identity
ecosystem: systemd
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

systemd `get_paths_from_environ` can keep the identity of the **current working directory** as a unit search path after `SYSTEMD_UNIT_PATH` listed an empty `::` component and that listing should not have been a path. Unset, empty `""`, trailing `:`, and middle `::` are different identities. Empty components other than a trailing `:` are split into leftover `""` entries; `path_split_and_make_absolute` turns those into leftover cwd `.`.

On failing_ref `cad2c455ec1acff29a81421c58adbe0ffc191f65`:

```
static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":"); /* Whether to append the normal search paths after what's obtained
                                           from envvar */

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
```

`getenv` missing (`!e`) is unset. `e` pointing at `""` is empty-string. Trailing `:` means append built-in defaults. Middle `::` is not trailing-append. The FIXME is unenforced. Empty components become leftover cwd search-path identity.

Public PR (systemd/systemd#43355). Tests after the repair: unset → default search path; `""` → empty search path; `:` → same as unset (append defaults); `:foo` and `/foo::/bar` → EINVAL; trailing `/foo:` → `/foo` plus defaults.

In-tree after the repair (not on failing_ref): `path_is_valid_search_path` requires `isempty(path) || (isempty(startswith(path, ":")) && !strstr(path, "::"))`. Leading/middle empty is `-EINVAL`. Generator path parse errors propagate instead of becoming leftover empty generator paths.

Case A — `SYSTEMD_UNIT_PATH` unset:
  default search-path identity
  not leftover-cwd

Case B — `SYSTEMD_UNIT_PATH=/foo::/bar`, leftover empty component:
  leftover: cwd `.` as a search path
  empty `::` component split then made absolute
  same process lookup

Case C — `SYSTEMD_UNIT_PATH=""` (set, empty string):
  empty search path
  not leftover cwd; not default path

Case D — `SYSTEMD_UNIT_PATH=/foo:` (trailing colon):
  `/foo` plus built-in defaults
  not leftover cwd

Case E — leading/middle empty rejected (post-repair shape, not on failing_ref):
  EINVAL
  not leftover cwd search path

The developer wants to know which identity case B actually used for the unit search path after `::`: leftover cwd `.` (empty component made absolute), current listed directories only, empty search path, or omitted (defaults).
""",
        observed="""# OBSERVED

Public systemd/systemd#43355 (merged 2026-08-13). Squash `f4284e9cebac67ad7af3bc27b736cf1107b88127` (parent `cad2c455ec1acff29a81421c58adbe0ffc191f65`). Follow-up for `cf7d80a5fe549d4db11800015e02220dccec3096` (SYSTEMD_UNIT_PATH colon-separated prepend/append). Local systemd was not performed on this lab host.

PR title: path-lookup: reject empty env path components. Only trailing empty components have special meaning: they request appending the built-in defaults. Share validation between path lookup and systemd-analyze verify.

On failing_ref, `get_paths_from_environ` documents the FIXME and still splits empty components. Unset vs empty `""` vs `:` vs `::` are different getenv identities; empty components become leftover cwd.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty-override. compose leftover listed-without-equals vs image ENV (packed this tick as leftover empty-vs-unset environment, not PATH cwd).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref cad2c455ec1acff29a81421c58adbe0ffc191f65
# src/libsystemd/sd-path/path-lookup.c get_paths_from_environ

# public shape:
# leftover cwd search path after SYSTEMD_UNIT_PATH=/foo::/bar
# unset is default path; "" is empty path; trailing : appends defaults
# new process / EINVAL after repair does not keep leftover cwd
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""systemd/systemd
  src/libsystemd/sd-path/path-lookup.c
  src/test/test-path-lookup.c
  src/analyze/analyze-verify-util.c
""",
        source="""repository: systemd/systemd
issue: https://github.com/systemd/systemd/pull/43355
pr: https://github.com/systemd/systemd/pull/43355
failing_ref (parent of squash on main): cad2c455ec1acff29a81421c58adbe0ffc191f65
fixed_ref (reject leading/middle empty path components): f4284e9cebac67ad7af3bc27b736cf1107b88127
merged_at: 2026-08-13T15:27:10Z
pr_author: lionheartyu
merged_by: yuwata
changed_files: src/libsystemd/sd-path/path-lookup.c, src/libsystemd/sd-path/path-lookup.h, src/libsystemd/sd-path/sd-path.c, src/core/manager.c, src/analyze/analyze-verify-util.c, src/analyze/test-verify.c, src/test/test-path-lookup.c
pr_title: path-lookup: reject empty env path components
scout_note: not 010/031 env-empty-vs-unset. leftover cwd search-path identity from empty :: component. unique vs 001-148.
""",
        answer_key="""KNOWN FIX (sealed): systemd/systemd PR 43355 squash f4284e9cebac67ad7af3bc27b736cf1107b88127.

failing_ref is parent cad2c455ec1acff29a81421c58adbe0ffc191f65.

get_paths_from_environ split empty SYSTEMD_UNIT_PATH components. Middle `::` became leftover cwd `.` in the unit search path. Unset / empty / trailing-colon / `::` were different identities; only trailing colon is append-defaults.

PR repair: path_is_valid_search_path rejects leading `:` and `::`. Generator path parse errors propagate.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unset defaults vs leftover cwd after :: vs empty string vs trailing-colon append vs EINVAL)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — unset, empty, trailing colon, and empty :: component are different identities; leftover cwd stayed a search path
ecosystem: systemd / path-lookup
mechanism_family: leftover-empty-vs-unset, empty-path-component-as-cwd, search-path-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "path_lookup_failing.c": """/* Reduced excerpt of get_paths_from_environ on failing_ref
 * src/libsystemd/sd-path/path-lookup.c
 * cad2c455ec1acff29a81421c58adbe0ffc191f65
 * empty :: components are split then made absolute as leftover cwd.
 */

static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":");

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  systemd get_paths_from_environ SYSTEMD_UNIT_PATH
  leftover cwd search path after empty :: component

Case A (unset SYSTEMD_UNIT_PATH):
  default search-path identity
  not leftover-cwd

Case B (/foo::/bar, leftover empty component):
  leftover: cwd . as a search path
  empty :: split then made absolute

Case C ("" empty string):
  empty search path
  not leftover cwd; not default path

Case D (/foo: trailing colon):
  /foo plus built-in defaults
  not leftover cwd

Case E (leading/middle empty rejected):
  EINVAL
  not leftover cwd search path

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  compose leftover listed-without-equals vs image ENV (this-tick compose packet)
""",
        },
    )


PACKETS = [
    (None, "hdd-compenv", packet_compose,
     "compose leftover listed-without-equals drops FOO; leftover image ENV; not 010/031"),
    (None, "hdd-sdpath", packet_systemd,
     "systemd leftover empty PATH :: component as cwd; not 010/031"),
]


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        return
    if job.get("status") == "READY":
        job["status"] = "CLAIMED"
        job["claimed_at"] = now_jst()
        job["worker"] = worker
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
    elif job.get("status") == "CLAIMED":
        old = job.get("worker")
        if old not in {None, worker} and not str(old).startswith("scout-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _init_trial(trial: str, seed: str) -> None:
    script = RUN_DIR / "scripts" / "init_trial.sh"
    subprocess.run([str(script), trial, seed], check=True, cwd=str(RUN_DIR))


def _complete_and_enqueue(packed: list[tuple[str | None, str, str, str]]) -> str:
    note = {"reason": ""}

    def fn(state):
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, jid, WORKER)
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            if job_id:
                job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
                if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                    if job.get("status") == "READY":
                        _claim_job(state, job_id, WORKER)
                    complete(state, job_id, result="ok", artifact=f"specimens/{spec_id}")
            already = any(
                j.get("queue") == "READY_R1_DREAM"
                and j.get("specimen") == spec_id
                and j.get("status") in {"READY", "CLAIMED"}
                for j in state.get("ready_jobs") or []
            )
            if not already:
                enqueue(
                    state,
                    "READY_R1_DREAM",
                    input_ref=f"seeds/{spec_id}.md trial={trial}",
                    expected_output="0001-dreamer.md",
                    kill_condition="15m",
                    estimated_cost="r1",
                    priority_reason=priority_reason,
                    specimen=spec_id,
                    lineage=trial,
                    phase="cambrian",
                    extra={"trial": trial},
                )
            reasons.append(f"READY_R1_DREAM trial={trial} specimen={spec_id}")
        existing_inputs = {
            j.get("input")
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_SPECIMEN_SCOUT"
        }
        for input_ref, reason in NEXT_SCOUTS:
            if input_ref in existing_inputs:
                continue
            enqueue(
                state,
                "READY_SPECIMEN_SCOUT",
                input_ref=input_ref,
                expected_output="specimens/specimen-NNN leftover-identity packet",
                kill_condition="25m no unique leftover-identity pair; skip bazel#29298; never overwrite 075",
                estimated_cost="low",
                priority_reason=reason,
                phase="cambrian",
            )
        note["reason"] = "; ".join(reasons)
        return True

    with_state(fn)
    return note["reason"]


def main() -> None:
    claimed: list[str] = []
    packed: list[tuple[str | None, str, str, str]] = []
    try:
        for job_id, trial, builder, priority_reason in PACKETS:
            spec_id = _claim_id()
            claimed.append(spec_id)
            emit(builder(spec_id))
            seed = write_seed(SPECIMENS / spec_id)
            _init_trial(trial, str(seed))
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
            print(f"hdd={HDD_ROOT / trial}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
        for jid, artifact in SKIP_JOBS.items():
            print(f"SKIP {jid}: {artifact}")
    except Exception:
        for spec_id in claimed:
            dest = SPECIMENS / spec_id
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
