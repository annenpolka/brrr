#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (buildkit git keep-git-dir cache key omits ref).

moby/buildkit#5444. shaToCacheKey was sha + optional .git; two named refs at the
same commit reused one keep-git-dir snapshot whose .git lacked the second ref.
Distinct from specimen-066 (moby healthcheck StartPeriod vs StartInterval).
Distinct from specimen-007 (libgit2). Distinct from specimen-091 (cargo PathBuf ..).
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0337"
WORKER = "scout-job-0337"
TRIAL = "hdd-gitrefkey"
START_N = 96


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 140):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: moby/buildkit
failing_ref: bc6f7be35057d15f8384c91ed500a610ab7e2a87
fixed_ref: 94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9
source_issue: https://github.com/moby/buildkit/issues/4446
source_pr: https://github.com/moby/buildkit/pull/5444
mechanism_tags:
  - git-keep-git-dir-cache-key
  - omitted-ref-from-sha-key
  - leftover-git-dir-without-ref
ecosystem: go
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

BuildKit's git source cache key for a checkout can be only the commit SHA (plus `.git` when `keepGitDir` is true). Two identifiers that name the **same commit through different refs** then share one snapshot. With `keepGitDir`, the program later resolves the user-provided ref inside that snapshot's `.git`. The first fetch may have stored a `.git` that does not contain the second ref.

In-tree after the repair: `TestMultipleTagAccessKeepGitDir` (`source/git/source_test.go`). Repo has tags `a/v1.2.3` and `a/v1.2.3-same` on the same initial commit. First identifier uses Ref `a/v1.2.3`; second uses `a/v1.2.3-same`. Same remote. `KeepGitDir` true vs false.

On failing_ref `bc6f7be35057d15f8384c91ed500a610ab7e2a87`, `shaToCacheKey` is:

```
func (gs *gitSourceHandler) shaToCacheKey(sha string) string {
	key := sha
	if gs.src.KeepGitDir {
		key += ".git"
	}
	if gs.src.Subdir != "" {
		key += ":" + gs.src.Subdir
	}
	return key
}
```

`CacheKey` after resolving ls-remote always calls `shaToCacheKey(sha)` with no ref. A commit-SHA identifier also keys only on the SHA.

Case A — `KeepGitDir` false, two tags on one commit (`a/v1.2.3` then `a/v1.2.3-same`):
  tree content is identical
  cache keys are equal (SHA only, length 40)
  no leftover `.git` identity (there is no `.git` in the snapshot)

Case B — `KeepGitDir` true, same two tags, same commit:
  pin (resolved SHA) is equal
  failing_ref cache keys are equal (`sha + ".git"`)
  second snapshot can reuse the first keep-git-dir checkout
  that `.git` was fetched for `a/v1.2.3`; `git rev-parse a/v1.2.3-same` inside it can miss the second ref

Case C — `KeepGitDir` true, identifier is a raw 40-char commit SHA (no named ref):
  `shaToCacheKey` still SHA + `.git`
  no named ref is requested in `.git` beyond the SHA fetch
  not the two-tag leftover

Case D — `KeepGitDir` true, two different commits (different SHAs):
  keys differ because SHA differs
  not a leftover-ref problem

The developer wants to know, for case B, which identity `shaToCacheKey` stored: leftover SHA-only (plus `.git`) so two refs collide, SHA#ref so they split, or omitted (no keep-git-dir key).
""",
        observed="""# OBSERVED

Public moby/buildkit PR 5444 (tonistiigi, merged 2024-10-28, merge `94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9`). Related discussion: #4446 (keep-git-dir detached HEAD / missing refs). Failing world pinned on merge first parent `bc6f7be35057d15f8384c91ed500a610ab7e2a87`. Local BuildKit execution was not performed on this lab host.

PR body: when keep-git-dir is true, a Git commit accessed through different refs (or a ref added after the commit was already pulled) reused a cache key that was only the git commit. The previous `.git` directory can be reused without the later ref inside. keep-git-dir false is unchanged: two refs at one commit yield identical tree content. A raw SHA identifier still does not add a named ref to the key.

In-tree test added on the PR (`TestMultipleTagAccessKeepGitDir`): two tags on the same commit; keep-git-dir true requires `key1 != key2` while `pin1 == pin2`; keep-git-dir false requires `key1 == key2`. That test is **not** on the failing revision.

`CacheKey` on failing_ref: if `gs.src.Ref` is already a commit SHA, `shaToCacheKey(ref)` (no extra ref). Otherwise `git ls-remote origin <ref> <ref>^{}` picks a SHA from HEAD/tag/partial lines, then `shaToCacheKey(sha)` with no usedRef.

Not this packet: specimen-066 (moby healthcheck StartPeriod vs StartInterval). specimen-007 (libgit2). specimen-091 (cargo git checkout PathBuf `..`). cargo#17289 (checkout short-id vs core.abbrev).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref bc6f7be35057d15f8384c91ed500a610ab7e2a87
# source/git/source.go shaToCacheKey / CacheKey
# source/git/source_test.go TestMultipleTagAccessKeepGitDir (on the PR, not failing_ref)

# public shape (keepGitDir, two tags, one commit):
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3"}
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3-same"}
# failing: CacheKey equal (sha+".git"); Snapshot 2 can reuse Snapshot 1 .git
# intended: pin equal, key unequal when keepGitDir
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""moby/buildkit
  source/git/source.go
  source/git/source_test.go
""",
        source="""repository: moby/buildkit
issue: https://github.com/moby/buildkit/issues/4446
pr: https://github.com/moby/buildkit/pull/5444
failing_ref (merge first parent): bc6f7be35057d15f8384c91ed500a610ab7e2a87
fixed_ref (merge commit): 94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9
pr_head: 44b1aca26a97107190c6b89e8277183e12ad17a0
second_parent: 44b1aca26a97107190c6b89e8277183e12ad17a0
merged_at: 2024-10-28T16:42:24Z
merged_by: tonistiigi
pr_author: tonistiigi
changed_files: source/git/source.go, source/git/source_test.go
pr_title: git: fix caching git commit through multiple refs
milestone: v0.17.0
scout_note: not specimen-066 (moby healthcheck timers). not specimen-007 libgit2. not specimen-091 cargo RecursivePathSource PathBuf. Distinct leftover: keep-git-dir cache key omitted the named ref so two tags at one SHA reused a .git without the second ref.
""",
        answer_key="""KNOWN FIX (sealed): moby/buildkit PR 5444 merge 94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9.

failing_ref is merge first parent bc6f7be35057d15f8384c91ed500a610ab7e2a87.

shaToCacheKey took only sha (+ ".git" if KeepGitDir, + ":" + subdir). CacheKey never passed the ls-remote usedRef. Two named refs at one commit therefore shared one keep-git-dir snapshot whose .git was fetched for the first ref.

Repair: shaToCacheKey(sha, ref) appends "#" + ref when KeepGitDir and ref != "". CacheKey records usedRef from ls-remote (partial/HEAD/tag). Commit-SHA identifiers still pass ref "". Added TestMultipleTagAccess / TestMultipleTagAccessKeepGitDir (two tags a/v1.2.3 and a/v1.2.3-same; keepGitDir requires key1 != key2, pin equal). keepGitDir false still keys equal. Existing keep-git-dir clones can miss after the key change.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (keepGitDir false same-key identical trees vs keepGitDir true SHA-only leftover vs SHA identifier with no named ref vs two different commits)
reproducibility: source-backed PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — pin (commit) and cache key are different objects; keep-git-dir snapshot identity included .git bytes that name refs the key omitted
ecosystem: go / buildkit / git source
mechanism_family: omitted-ref-from-cache-key, keep-git-dir-snapshot, two-refs-one-sha

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "sha_to_cache_key_failing.go": """// Reduced excerpt of shaToCacheKey on failing_ref
// source/git/source.go
// bc6f7be35057d15f8384c91ed500a610ab7e2a87
// Key is commit SHA. KeepGitDir adds ".git". Named ref is not in the key.

func (gs *gitSourceHandler) shaToCacheKey(sha string) string {
	key := sha
	if gs.src.KeepGitDir {
		key += ".git"
	}
	if gs.src.Subdir != "" {
		key += ":" + gs.src.Subdir
	}
	return key
}
""",
            "cache_key_failing.go": """// Reduced excerpt of CacheKey on failing_ref
// source/git/source.go
// After ls-remote picks a SHA, key is shaToCacheKey(sha) with no usedRef.
// Commit-SHA identifier also keys only on the SHA.

	if ref := gs.src.Ref; ref != "" && gitutil.IsCommitSHA(ref) {
		cacheKey := gs.shaToCacheKey(ref)
		gs.cacheKey = cacheKey
		return cacheKey, ref, nil, true, nil
	}
	// ...
	cacheKey := gs.shaToCacheKey(sha)
	gs.cacheKey = cacheKey
	return cacheKey, sha, nil, true, nil
""",
            "leftover_identity_split.txt": """Registry / fixture:
  two tags on one commit: a/v1.2.3 and a/v1.2.3-same
  GitIdentifier.Remote shared
  pin = resolved commit SHA (40 hex)

Case A (KeepGitDir false, two tags, one commit):
  tree bytes identical
  cache key = SHA (len 40)
  keys equal
  no .git in snapshot

Case B (KeepGitDir true, two tags, one commit):
  pin equal
  failing_ref key = SHA + ".git" for both (keys equal)
  second snapshot can reuse first .git
  leftover: named ref omitted from key; .git may lack a/v1.2.3-same

Case C (KeepGitDir true, identifier is raw commit SHA):
  key = SHA + ".git"
  no named ref requested
  not the two-tag leftover

Case D (KeepGitDir true, two different commits):
  SHA differs so keys differ
  not leftover-ref

Not this packet:
  moby healthcheck StartPeriod vs StartInterval (specimen-066)
  libgit2 (specimen-007)
  cargo git checkout PathBuf with .. (specimen-091)
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == JOB_ID), None)
        if job is None:
            raise SystemExit(f"{JOB_ID} missing")
        if job.get("status") == "CLAIMED" and job.get("worker") == WORKER:
            complete(state, JOB_ID, result="ok", artifact=f"specimens/{spec_id}")
        elif job.get("status") == "DONE" and job.get("artifact") == f"specimens/{spec_id}":
            pass
        else:
            raise SystemExit(
                f"{JOB_ID} status={job.get('status')} worker={job.get('worker')} artifact={job.get('artifact')}"
            )
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
                priority_reason="buildkit keep-git-dir cache key omitted named ref; not 066/007/091",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        for q, inp, reason in (
            (
                "READY_SPECIMEN_SCOUT",
                "public OSS: bazel env_inherit local vs remote cache key not 29298-unfixed if a pinned fix exists",
                "bazel cache key identity",
            ),
            (
                "READY_SPECIMEN_SCOUT",
                "public OSS: pip extras leftover identity not pipmark/080",
                "pip extras leftover",
            ),
        ):
            exists = any(j.get("input") == inp and j.get("status") in {"READY", "CLAIMED"} for j in state["ready_jobs"])
            if not exists:
                enqueue(
                    state,
                    q,
                    input_ref=inp,
                    expected_output="packet or skip",
                    kill_condition="20m",
                    estimated_cost="low",
                    priority_reason=reason,
                    phase="cambrian",
                )
        note["reason"] = f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id} (not launched; R1 slots occupied)"
        return spec_id

    with_state(fn)
    return note["reason"]


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        launch_note = _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(launch_note)
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
