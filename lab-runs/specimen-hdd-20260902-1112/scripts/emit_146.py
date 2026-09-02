#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 146-147.

Packed (unique vs 001-145; 075 not overwritten; not bazel#29298):
1) job-0621 saltstack/salt#69941 / PR 69943:
   leftover RSA private-key object after on-disk rotation because
   get_rsa_key memoized on (path, passphrase) and omitted mtime.
2) job-0622 aws/aws-cdk PR 21374:
   leftover asset content fingerprint after rewrite because the
   large-file fingerprint cache keyed on getUTCDate() (day-of-month)
   + getUTCMilliseconds() instead of full mtime.

SKIP:
- job-0623 / job-0628 packer leftover cache vs config/template:
  packer#8394 is iso_target_path cache *location*, not leftover
  identity after template/config change. #9595 wontfix checksum
  rename. not inventing refs; not 118.
- job-0627 pulumi leftover checkpoint vs stack: no merged leftover-
  identity pair this tick. not inventing refs; not 081/118.
- job-0629 opentofu leftover state serial vs identity: #4114 closed
  not_planned (omitted lineage/serial fields, not leftover serial).
  not inventing refs; not 081/118.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 146
WORKER = "scout-coord-2110"
SKIP_JOBS = {
    "job-0623": (
        "skip packer leftover cache vs config identity: packer#8394 is "
        "iso_target_path cache location not leftover-identity; #9595 "
        "wontfix. not inventing refs; not 118"
    ),
    "job-0627": (
        "skip pulumi leftover checkpoint vs stack identity: no merged "
        "leftover-identity pair this tick. not inventing refs; not 081/118"
    ),
    "job-0628": (
        "skip packer leftover cache vs template identity: no merged leftover-"
        "HIT omitted-key pair; #8394 is cache location. not inventing refs; "
        "not 001-145"
    ),
    "job-0629": (
        "skip opentofu leftover state serial vs identity: tofu#4114 closed "
        "not_planned (omitted lineage/serial fields, not leftover serial). "
        "not inventing refs; not 081/118"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: conan leftover package cache vs recipe identity not 136",
        "unique conan leftover if pinned",
    ),
    (
        "public OSS: nomad leftover artifact vs job identity not 118",
        "unique nomad leftover if pinned",
    ),
    (
        "public OSS: dagger leftover cache vs env identity not 075",
        "unique dagger leftover if pinned",
    ),
    (
        "public OSS: sccache leftover CPATH identity if #2798 merges",
        "unique sccache leftover if pinned",
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


def packet_salt(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: saltstack/salt
failing_ref: 6e83268b7001de0b4847f8623791b9363a83d103
fixed_ref: 6cf49f5364e5e716852a747682196646c8af1801
source_issue: https://github.com/saltstack/salt/issues/69941
source_pr: https://github.com/saltstack/salt/pull/69943
mechanism_tags:
  - leftover-rsa-key
  - omitted-mtime-from-memoize-key
  - process-cache-after-rotation
ecosystem: salt
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Salt `salt.crypt.get_rsa_key(path, passphrase)` can keep the identity of a **previous RSA private key** after the file on disk was rotated and the loaded key should have been different. The memoize cache is keyed on `(path, passphrase)` only. On-disk mtime is not part of that key. A rewritten `minion.pem` in the same process still returns the leftover previous key object until the process restarts.

On failing_ref `6e83268b7001de0b4847f8623791b9363a83d103`:

```
@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    \"\"\"
    Read a private key off the disk. we memoize the constructed private key
    based on the input args.
    \"\"\"
    return PrivateKey.from_file(path, passphrase).key
```

`salt.utils.decorators.memoize` is a plain str-keyed dict. Path and passphrase are not the file identity. `_auth_singleton_key` still threads `str(os.path.getmtime(keypath))` for a *different* cache and does not compensate.

Public report (saltstack/salt#69941). Write PEM; `get_rsa_key`; rewrite PEM and bump mtime; second `get_rsa_key` returns leftover previous public bytes. 3006.x two-layer helper memoized `(path, mtime, passphrase)` and evicted.

In-tree after the repair (not on failing_ref): `_get_key_with_evict(path, timestamp, passphrase)` is the memoized function; `get_rsa_key` supplies `str(os.path.getmtime(path))`.

Case A — second call, same file, same mtime:
  cache identity is current
  not leftover-after-rotation

Case B — file rewritten, leftover memoize hit:
  leftover: previous RSA private-key object / previous public bytes
  mtime omitted from memoize key
  same process

Case C — new process / memoize cache empty:
  fresh key identity
  not leftover previous key

Case D — memoize key includes mtime (post-repair shape, not on failing_ref):
  new key material after rotation
  not leftover previous key

The developer wants to know which identity case B actually used for the private key after the file change: leftover previous-memoize object (mtime omitted), current on-disk key, or omitted (no cache).
""",
        observed="""# OBSERVED

Public saltstack/salt#69941 (closed 2026-08-31). PR 69943 squash `6cf49f5364e5e716852a747682196646c8af1801` (parent `6e83268b7001de0b4847f8623791b9363a83d103`). Local salt was not performed on this lab host.

Issue body: 3008.x PKI refactor collapsed the two-layer helper into a single decorated `get_rsa_key(path, passphrase)`. Rotated key file; same process; leftover previous key until restart. Reproduction writes two PEMs with `os.utime` and asserts public bytes differ.

On failing_ref, `@memoize` keys only path+passphrase. Nested `_auth_singleton_key` still has mtime for AsyncAuth and is a different cache.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-139 black leftover project-root vs omitted CWD on lru_cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 6e83268b7001de0b4847f8623791b9363a83d103
# salt/crypt.py get_rsa_key / PrivateKey.from_file

# public shape:
# leftover RSA key object after on-disk rotation
# memoize key is (path, passphrase); mtime omitted
# new process yields the new key
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""saltstack/salt
  salt/crypt.py
  salt/utils/decorators/__init__.py
""",
        source="""repository: saltstack/salt
issue: https://github.com/saltstack/salt/issues/69941
pr: https://github.com/saltstack/salt/pull/69943
failing_ref (parent of squash on 3008.x): 6e83268b7001de0b4847f8623791b9363a83d103
fixed_ref (restore mtime eviction helper): 6cf49f5364e5e716852a747682196646c8af1801
merged_at: 2026-08-09T05:20:15Z
pr_author: dwoz
merged_by: dwoz
changed_files: salt/crypt.py, tests/pytests/unit/crypt/test_crypt_cryptography.py, changelog/69941.fixed.md
pr_title: Restore mtime-based eviction on get_rsa_key
scout_note: not 136 pants process cache / not 139 black CWD lru. leftover RSA key after rotation because mtime omitted from memoize key. unique vs 001-145.
""",
        answer_key="""KNOWN FIX (sealed): saltstack/salt PR 69943 squash 6cf49f5364e5e716852a747682196646c8af1801.

failing_ref is parent 6e83268b7001de0b4847f8623791b9363a83d103.

get_rsa_key was @memoize on (path, passphrase) only. Rotated PEM kept leftover previous key object in-process. mtime was not part of the memoize identity.

PR repair: restore _get_key_with_evict(path, timestamp, passphrase) as the memoized helper; get_rsa_key passes str(os.path.getmtime(path)).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged file vs leftover key after rotation vs new process vs mtime in memoize key)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — file path and on-disk key material are different identities; leftover memoize object stayed current
ecosystem: salt / crypt RSA cache
mechanism_family: leftover-rsa-key, omitted-mtime-from-memoize-key, process-cache-after-rotation

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "rsa_key_failing.py": """# Reduced excerpt of get_rsa_key memoize on failing_ref
# salt/crypt.py
# 6e83268b7001de0b4847f8623791b9363a83d103
# memoize key is (path, passphrase). mtime omitted.
# leftover previous key object after PEM rotation in-process.

@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    return PrivateKey.from_file(path, passphrase).key

# _auth_singleton_key still has mtime for a *different* cache
# and does not evict get_rsa_key
""",
            "leftover_identity_split.txt": """Registry / fixture:
  salt.crypt.get_rsa_key process memoize
  leftover RSA key after on-disk rotation

Case A (second call, same file, same mtime):
  current cache identity
  not leftover-after-rotation

Case B (PEM rewritten, leftover memoize hit):
  leftover: previous RSA private-key object
  mtime omitted from memoize key
  same process

Case C (new process / empty memoize):
  fresh key identity
  not leftover previous key

Case D (memoize key includes mtime):
  new key after rotation
  not leftover previous key

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  black leftover project-root vs omitted CWD (specimen-139)
""",
        },
    )


def packet_cdk(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: aws/aws-cdk
failing_ref: fc8d54e866ab313b6b25b80039dff03e47d0a88c
fixed_ref: 65a210aaaf8f45095170bca7779fd274aab54a00
source_issue: https://github.com/aws/aws-cdk/issues/21374
source_pr: https://github.com/aws/aws-cdk/pull/21374
mechanism_tags:
  - leftover-fingerprint
  - truncated-mtime-cache-key
  - large-file-fingerprint-cache
ecosystem: aws-cdk
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

AWS CDK `contentFingerprint` can keep the identity of a **previous file content hash** after the file was rewritten and the fingerprint should have been different. The large-file fingerprint cache key uses `stats.mtime.getUTCDate()` (day-of-month only) and `stats.mtime.getUTCMilliseconds()` (0–999 ms), plus inode and size. Full mtime is not the cache identity. A same-size rewrite on the same inode that collides on day-of-month and milliseconds still returns the leftover previous sha256.

On failing_ref `fc8d54e866ab313b6b25b80039dff03e47d0a88c`:

```
const stats = fs.statSync(file, { bigint: true });
const cacheKey = JSON.stringify({
  mtime_unix: stats.mtime.getUTCDate(),
  mtime_ms: stats.mtime.getUTCMilliseconds(),
  inode: stats.ino.toString(),
  size: stats.size.toString(),
});
return fingerprintCache.obtain(cacheKey, () => contentFingerprintMiss(file));
```

`getUTCDate()` is the day of the month, not unix time. `getUTCMilliseconds()` is the millisecond-of-second, not epoch ms. Introduced with the large-asset fingerprint cache.

Public report (aws/aws-cdk#21374). Fingerprint a file; rewrite contents; second fingerprint can match the leftover previous hash when truncated mtime collides. In-tree test after the repair forces `utimes` to Date(1337) so hash1 != hash2 even when tests run fast.

In-tree after the repair (not on failing_ref): `mtime_unix: stats.mtime.toUTCString()`, `mtime_ms: stats.mtimeMs.toString()`.

Case A — second fingerprint, same bytes, same full mtime:
  cache identity is current
  not leftover-after-rewrite

Case B — contents rewritten, leftover cache hit:
  leftover: previous sha256 fingerprint
  full mtime omitted (day-of-month + ms-of-second only)
  same inode and size

Case C — cache cleared / process restart / Node < 12 bypass:
  fresh content identity
  not leftover previous hash

Case D — full mtime in cache key (post-repair shape, not on failing_ref):
  new hash after rewrite
  not leftover previous fingerprint

The developer wants to know which identity case B actually used for the fingerprint after the rewrite: leftover previous-cache hash (truncated mtime), current content hash, or omitted (no cache).
""",
        observed="""# OBSERVED

Public aws/aws-cdk#21374 (merged 2022-07-29). PR 21374 squash `65a210aaaf8f45095170bca7779fd274aab54a00` (parent `fc8d54e866ab313b6b25b80039dff03e47d0a88c`). Local aws-cdk was not performed on this lab host.

PR body: fingerprint cache invalidation incorrectly uses mtime; only day-of-month and fractional seconds. Introduced in #21321 large-asset fingerprint cache.

On failing_ref, `contentFingerprint` builds cacheKey from getUTCDate + getUTCMilliseconds + inode + size, then `fingerprintCache.obtain`. Tests after the repair bump mtime to Date(1337) because fast rewrites collide.

Not this packet: specimen-139 black leftover project-root vs omitted CWD. specimen-075 rustc incremental fingerprint. specimen-090 webpack leftover.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref fc8d54e866ab313b6b25b80039dff03e47d0a88c
# packages/@aws-cdk/core/lib/fs/fingerprint.ts contentFingerprint

# public shape:
# leftover sha256 fingerprint after same-size rewrite
# cache key uses getUTCDate + getUTCMilliseconds, not full mtime
# cache clear / full mtime key yields the new hash
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""aws/aws-cdk
  packages/@aws-cdk/core/lib/fs/fingerprint.ts
""",
        source="""repository: aws/aws-cdk
issue: https://github.com/aws/aws-cdk/issues/21374
pr: https://github.com/aws/aws-cdk/pull/21374
failing_ref (parent of squash on main): fc8d54e866ab313b6b25b80039dff03e47d0a88c
fixed_ref (full mtime in fingerprint cache key): 65a210aaaf8f45095170bca7779fd274aab54a00
merged_at: 2022-07-29T13:33:43Z
pr_author: RomainMuller
merged_by: RomainMuller
changed_files: packages/@aws-cdk/core/lib/fs/fingerprint.ts, packages/@aws-cdk/core/test/fs/fs-fingerprint.test.ts
pr_title: fix(core): asset fingerprint cache invalidation incorrectly uses mtime
scout_note: not 139 black CWD lru / not 075 rustc fingerprint. leftover content hash after rewrite because truncated mtime was the cache identity. unique vs 001-145.
""",
        answer_key="""KNOWN FIX (sealed): aws/aws-cdk PR 21374 squash 65a210aaaf8f45095170bca7779fd274aab54a00.

failing_ref is parent fc8d54e866ab313b6b25b80039dff03e47d0a88c.

contentFingerprint cached on getUTCDate() (day-of-month) + getUTCMilliseconds() + inode + size. Same-size rewrite could keep leftover previous sha256.

PR repair: mtime_unix = stats.mtime.toUTCString(); mtime_ms = stats.mtimeMs.toString().

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged file vs leftover fingerprint after rewrite vs cache bypass vs full mtime key)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — inode/size/truncated-mtime and file bytes are different identities; leftover sha256 stayed current
ecosystem: aws-cdk / asset fingerprint cache
mechanism_family: leftover-fingerprint, truncated-mtime-cache-key, large-file-fingerprint-cache

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "fingerprint_failing.ts": """// Reduced excerpt of contentFingerprint cache on failing_ref
// packages/@aws-cdk/core/lib/fs/fingerprint.ts
// fc8d54e866ab313b6b25b80039dff03e47d0a88c
// cache key uses getUTCDate (day-of-month) + getUTCMilliseconds.
// leftover previous sha256 after same-size rewrite.

const stats = fs.statSync(file, { bigint: true });
const cacheKey = JSON.stringify({
  mtime_unix: stats.mtime.getUTCDate(),
  mtime_ms: stats.mtime.getUTCMilliseconds(),
  inode: stats.ino.toString(),
  size: stats.size.toString(),
});
return fingerprintCache.obtain(cacheKey, () => contentFingerprintMiss(file));
""",
            "leftover_identity_split.txt": """Registry / fixture:
  CDK contentFingerprint large-file cache
  leftover sha256 after same-size rewrite

Case A (second fingerprint, same bytes, same mtime):
  current cache identity
  not leftover-after-rewrite

Case B (contents rewritten, leftover cache hit):
  leftover: previous sha256 fingerprint
  full mtime omitted (day-of-month + ms-of-second)
  same inode and size

Case C (cache cleared / Node < 12 bypass):
  fresh content identity
  not leftover previous hash

Case D (full mtime in cache key):
  new hash after rewrite
  not leftover previous fingerprint

Not this packet:
  black leftover project-root vs omitted CWD (specimen-139)
  rustc incremental fingerprint (specimen-075)
""",
        },
    )


PACKETS = [
    ("job-0621", "hdd-saltrsa", packet_salt,
     "salt leftover RSA key omits mtime from memoize; not 136/139"),
    ("job-0622", "hdd-cdkmtime", packet_cdk,
     "cdk leftover fingerprint truncated mtime cache key; not 075/139"),
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
        if old not in {None, worker} and not str(old).startswith("scout-coord-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _claim_all() -> None:
    def fn(state):
        for jid in list({p[0] for p in PACKETS}) + list(SKIP_JOBS):
            _claim_job(state, jid, WORKER)
        return True

    with_state(fn)


def _complete_and_enqueue(packed: list[tuple[str, str, str, str]]) -> str:
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
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
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
    _claim_all()
    claimed: list[str] = []
    packed: list[tuple[str, str, str, str]] = []
    try:
        for job_id, trial, builder, priority_reason in PACKETS:
            spec_id = _claim_id()
            claimed.append(spec_id)
            emit(builder(spec_id))
            write_seed(SPECIMENS / spec_id)
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
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
