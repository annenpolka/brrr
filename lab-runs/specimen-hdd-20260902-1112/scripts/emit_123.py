#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packet 123.

Packed (unique vs 001-122; 075 not overwritten; not bazel#29298):
1) earthly/earthly PR 3810: leftover CACHE --id identity is the
   unexpanded ARG token. handleCache expands CACHE directory and mode
   but omits expandArgs on opts.ID; converter.Cache uses that literal
   as cacheID when GlobalCache is on. Distinct from specimen-115
   go-task leftover wildcard checksum omitting MATCH, specimen-119
   pixi leftover task-cache filename omitting args, 066/097 docker
   layer leftover.

SKIP (claimed job-0528..0531, no unique leftover-identity pair):
- job-0528 uv leftover extras marker vs lock: uv#20078 merged but
  materialization failed after discarding extras/group context; not
  leftover previous extras object reused. extraedge/080/058/006/102/106
  already cover extras/lock leftover axes. not inventing refs.
- job-0529 go work leftover use vs replace: already specimen-103.
- job-0530 npm leftover nested overrides: already specimen-095.
- job-0531 gradle CC leftover named files: already specimen-104.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 123
WORKER = "scout-coord-1804-0"
TRIAL = "hdd-cachearg"
SKIP_JOBS = {
    "job-0528": (
        "skip uv leftover extras marker vs lock identity: uv#20078 "
        "merged (f9074c50 parent 3f000eda) discards extras/group context "
        "so cached-tool materialization fails; not leftover previous extras "
        "object reused after extras change. extraedge/080/058/006/102/106 "
        "already cover extras/lock leftover. not inventing refs"
    ),
    "job-0529": (
        "skip go work leftover use vs replace identity: already "
        "specimen-103 go-work-sync-replace-leftover "
        "(failing a2214422 / fixed 8191cd88). not inventing refs"
    ),
    "job-0530": (
        "skip npm leftover nested overrides identity: already "
        "specimen-095 leftover-override-set nested-override-lockfile-identity "
        "(failing e345cc58 / fixed b9225e52 npm#5850 PR 8089). not inventing refs"
    ),
    "job-0531": (
        "skip gradle CC leftover named files vs 104 ccnamed: already "
        "specimen-104 named-file-collection-leftover-base-dir "
        "(failing 92fc3199 / fixed 2f46ab73 gradle#30052 PR 32359). not inventing refs"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: conan leftover package_id vs recipe revision not 001-122",
        "unique conan leftover package_id",
    ),
    (
        "public OSS: mill leftover zinc analysis vs 117 unique axis",
        "unique mill leftover zinc",
    ),
    (
        "public OSS: dart pub leftover package_config vs pubspec not 001-122",
        "unique dart pub leftover",
    ),
    (
        "public OSS: homebrew leftover bottle vs formula rebuild not 001-122",
        "unique brew leftover bottle",
    ),
    (
        "public OSS: cocoapods leftover Pods vs Podfile.lock not 122/102",
        "unique cocoapods leftover checkout",
    ),
    (
        "public OSS: opam leftover switch vs lock identity not 001-122",
        "unique opam leftover switch",
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


def packet_earthly(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: earthly/earthly
failing_ref: 6b297d587cc12bea0372ca333fef34b522388b34
fixed_ref: 892a4e03040feca16423d703a2a7ff0a380052cd
source_pr: https://github.com/earthly/earthly/pull/3810
mechanism_tags:
  - leftover-cache-mount-id
  - omitted-expanded-arg
  - unexpanded-cache-id-token
ecosystem: earthly
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Earthly's CACHE command can take `--id` so two targets share one cache mount.
On failing_ref `6b297d587cc12bea0372ca333fef34b522388b34`, `handleCache`
expands the CACHE directory and the CACHE mode through `expandArgs`, then
calls `converter.Cache` with `opts.ID` unchanged.

When the converter feature `GlobalCache` is on and `--id` is set,
`converter.Cache` sets:

```
cacheID = opts.ID
```

instead of the default `path.Join("/run/cache", cacheKey(c.target), mountTarget)`.

`opts.ID` is not passed through `expandArgs`. Public report (earthly/earthly#3810):

```
ARG something
CACHE --id $something
```

produces a cache id of the literal string `$something`. Changing the ARG
value does not change the cache identity, so a later ARG value reuses the
leftover mount from the previous ARG value.

Case A — first CACHE --id $something with ARG something=foo:
  cache mount written under identity `$something` (unexpanded token)
  not leftover yet

Case B — later CACHE --id $something with ARG something=bar, leftover foo mount:
  leftover: previous ARG value's cache mount
  expanded ARG omitted from cacheID
  public report: cache id stays the literal `$something`

Case C — CACHE --id with a constant distinct string ("foo" vs "bar"):
  two identities
  not this leftover

Case D — delete the cache mount then CACHE with ARG=bar:
  fresh identity
  not leftover cache id

The directory path of CACHE *is* expanded. Mode is expanded. Only `--id`
is omitted.

The developer wants to know, for case B, which cache-mount identity Earthly
actually used: leftover unexpanded `$something` from foo, an expanded
`bar` id, or omitted (no --id, target-keyed default).
""",
        observed="""# OBSERVED

Public earthly/earthly#3810 merged 2024-02-16. Squash `892a4e03040feca16423d703a2a7ff0a380052cd` (parent `6b297d587cc12bea0372ca333fef34b522388b34`). Local earthly was not performed on this lab host.

PR body: ARGs were not expanded in `--id` of CACHE; example `ARG something` / `CACHE --id $something` resulted in cache id of the literal string `$something`.

On failing_ref, `earthfile2llb/interpreter.go` `handleCache` expands `args[0]` (directory) and `opts.Mode`, then `i.converter.Cache(ctx, dir, opts)` with `opts.ID` untouched. `earthfile2llb/converter.go` `Cache` uses `opts.ID` as `cacheID` when `c.ftrs.GlobalCache && opts.ID != ""`.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH). Distinct leftover: Earthly CACHE --id identity is the unexpanded ARG token. Not specimen-119 (pixi leftover task-cache filename keyed by env+name omitting args). Not 066/097 docker/buildkit leftover layers.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 6b297d587cc12bea0372ca333fef34b522388b34
# earthfile2llb/interpreter.go handleCache
# earthfile2llb/converter.go Cache

# public shape:
# ARG something
# CACHE --id $something /id-test
# leftover cache mount identity is the unexpanded token
# later ARG something=bar reuses leftover foo mount
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""earthly/earthly
  earthfile2llb/interpreter.go
  earthfile2llb/converter.go
  tests/cache-cmd.earth
  tests/Earthfile
""",
        curation="""ACCEPT_R1

contrastiveness: high (first CACHE vs leftover mount after ARG change vs constant --id vs wipe cache)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — unexpanded ARG token identity and expanded ARG value identity are different objects; leftover mount blocked cache
ecosystem: earthly / buildkit cache mounts
mechanism_family: leftover-cache-id, omitted-expanded-arg, unexpanded-token

Packet is the failing world only. Do not assume a root cause.
""",
        source="""repository: earthly/earthly
pr: https://github.com/earthly/earthly/pull/3810
failing_ref (parent of squash on main): 6b297d587cc12bea0372ca333fef34b522388b34
fixed_ref (Expand args in CACHE --id): 892a4e03040feca16423d703a2a7ff0a380052cd
merged_at: 2024-02-16T19:30:45Z
pr_author: brandonSc
merged_by: brandonSc
changed_files: earthfile2llb/interpreter.go, tests/Earthfile, tests/cache-cmd.earth
pr_title: Expand args in CACHE --id
scout_note: not specimen-115 go-task leftover MATCH; not specimen-119 pixi leftover env+name filename omitting args; not 066/097 docker leftover. Distinct leftover: CACHE --id identity is unexpanded ARG token. job-idle-mine after skip 0528-0531.
""",
        answer_key="""KNOWN FIX (sealed): earthly/earthly PR 3810 squash 892a4e03040feca16423d703a2a7ff0a380052cd.

failing_ref is squash parent 6b297d587cc12bea0372ca333fef34b522388b34.

handleCache expanded CACHE directory and mode but omitted expandArgs on opts.ID. converter.Cache used that literal as cacheID when GlobalCache was on, so leftover previous ARG value's mount was reused.

PR repair: if opts.ID != "", opts.ID, err = i.expandArgs(ctx, opts.ID, false, false) before converter.Cache. Test test-id-expand-args writes with --ID_1=test then hits with --id $ID_2 expanded to test.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        files={
            "handle_cache_failing.go": """// Reduced excerpt of Interpreter.handleCache on failing_ref
// earthfile2llb/interpreter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// Directory and mode are expanded. opts.ID is not.

func (i *Interpreter) handleCache(ctx context.Context, cmd spec.Command) error {
	opts := commandflag.CacheOpts{}
	args, err := flagutil.ParseArgsCleaned("CACHE", &opts, flagutil.GetArgsCopy(cmd))
	dir, err := i.expandArgs(ctx, args[0], false, false)
	expandedMode, err := i.expandArgs(ctx, opts.Mode, false, false)
	opts.Mode = expandedMode
	if !path.IsAbs(dir) {
		dir = path.Clean(path.Join("/", i.converter.mts.Final.MainImage.Config.WorkingDir, dir))
	}
	if err := i.converter.Cache(ctx, dir, opts); err != nil {
		return i.wrapError(err, cmd.SourceLocation, "apply CACHE")
	}
	return nil
}
""",
            "converter_cache_id.go": """// Reduced excerpt of Converter.Cache on failing_ref
// earthfile2llb/converter.go
// 6b297d587cc12bea0372ca333fef34b522388b34
// When GlobalCache and --id are set, cache identity is opts.ID as parsed.

func (c *Converter) Cache(ctx context.Context, mountTarget string, opts commandflag.CacheOpts) error {
	key := cacheKey(c.target)
	cacheID := path.Join("/run/cache", key, path.Clean(mountTarget))
	if c.ftrs.GlobalCache && opts.ID != "" {
		cacheID = opts.ID
	}
	// ...
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  ARG something
  CACHE --id $something /id-test
  leftover cache mount identity = literal $something

Case A (first CACHE, ARG something=foo):
  writes cache under unexpanded token
  not leftover yet

Case B (later CACHE, ARG something=bar, leftover foo mount):
  leftover: foo cache under $something
  expanded ARG omitted from cacheID

Case C (CACHE --id foo vs CACHE --id bar constants):
  two identities
  not this leftover

Case D (delete cache mount then ARG=bar):
  fresh identity
  not leftover

Not this packet:
  go-task leftover wildcard fingerprint omitting MATCH (specimen-115)
  pixi leftover task-cache filename env+name omitting args (specimen-119)
  docker/buildkit leftover layers (066/097)
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") == "READY":
                job["status"] = "CLAIMED"
                job["worker"] = WORKER
                job["claimed_at"] = now_jst()
                complete(state, jid, result="skip", artifact=artifact)
            elif job.get("status") == "CLAIMED":
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        if spec_id not in ids:
            state.setdefault("specimens", []).append({"id": spec_id})
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
                input_ref=f"seeds/{spec_id}.md trial={TRIAL}",
                expected_output="0001-dreamer.md",
                kill_condition="15m",
                estimated_cost="r1",
                priority_reason=(
                    "earthly leftover CACHE --id unexpanded ARG token; "
                    "not 115/119/066/097"
                ),
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
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
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched from emit; READY_R1_DREAM already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = f"READY_R1_DREAM enqueued trial={TRIAL} specimen={spec_id}"
        # never touch destroyer-bindname-7 / job-0534
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        p = emit(packet_earthly(spec_id))
        s = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(p)
        print(s)
        print(launch_note)
        print(f"ids={spec_id} trial={TRIAL}")
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
