#!/usr/bin/env python3
"""Emit two sealed REAL_SOURCE_BACKED leftover-identity packets.

1) pytest-dev/pytest#12167 / PR 12168: leftover cache-dir identity omits
   supporting files (.gitignore / CACHEDIR.TAG). Unique vs 001-003.
2) npm/cli#9613 / PR 9632: leftover .bin shim identity after uninstall
   under install-strategy=linked. Not npm peer leftover 004/082/095.

job-0339 cargo git+ssh vs registry: no merged leftover pair
(#14526 closed without PR; #14466/#10756 not_planned; #13549 is SSH
error-message). job-0371 was coord-skip-dup vs 001-003; cache-dir leftover
is a different object. Not bazel#29298.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 105
WORKER_PY = "scout-job-0455"
WORKER_NPM = "scout-job-0339"
JOB_PY = "job-0455"
JOB_NPM = "job-0339"
TRIAL_PY = "hdd-pycachedir"
TRIAL_NPM = "hdd-npmlinkbin"
SKIP_JOBS = {
    "job-0453": (
        "skip go buildid leftover vs content: no merged pinned failing+fixed "
        "pair found; not inventing refs; not 084/103"
    ),
    "job-0454": (
        "skip cmake fileapi leftover vs target: no merged pinned pair; "
        "SKIP bazel#29298 unfixed"
    ),
}


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 160):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_pytest(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: pytest-dev/pytest
failing_ref: 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
fixed_ref: 5acc3f86ac1713aea6775f04dcae35a2f0848437
source_issue: https://github.com/pytest-dev/pytest/issues/12167
source_pr: https://github.com/pytest-dev/pytest/pull/12168
mechanism_tags:
  - leftover-cache-dir-identity
  - supporting-files-omitted
  - exists-gate-skips-gitignore
ecosystem: python
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7200
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

pytest's cache directory can keep the identity of an **already-initialized cache dir** after a write that only created the directory, even when the supporting files that mark that identity (`.gitignore`, `CACHEDIR.TAG`, `README.md`) were never written.

On failing_ref `4e3dd21506a9e543c04c63ebff966a9b604d2b9e`, `Cache.set` (`src/_pytest/cacheprovider.py`) decides whether to call `_ensure_supporting_files` with:

```
if path.parent.is_dir():
    cache_dir_exists_already = True
else:
    cache_dir_exists_already = self._cachedir.exists()
    path.parent.mkdir(exist_ok=True, parents=True)
if not cache_dir_exists_already:
    self._ensure_supporting_files()
```

`Cache.mkdir` creates `_cachedir/d/<name>` with `parents=True` and never calls `_ensure_supporting_files`. `_ensure_supporting_files` writes `README.md`, `.gitignore` (`# Created by pytest automatically.` plus `*`), and `CACHEDIR.TAG`.

Public report (pytest-dev/pytest#12167): the earlier check from PR 3982 is not robust. If a cache write is interrupted after the directory exists and is non-empty, `.pytest_cache` is present without `.gitignore`. Because `_cachedir.exists()` is then true, later `set` calls never write the supporting files.

Case A — first `Cache.set("cache/lastfailed", ...)` on an absent `.pytest_cache`:
  `path.parent` (`v/`) is not a dir
  `_cachedir.exists()` is false
  supporting files are written
  no leftover uninitialized dir identity

Case B — interrupt after `.pytest_cache/` (and maybe `v/`) exists, before supporting files:
  leftover: dir identity is "already initialized"
  `.gitignore` / `CACHEDIR.TAG` omitted
  later `set` sees exists() and skips `_ensure_supporting_files`

Case C — `Cache.mkdir("plugin-dump")` then `Cache.set(...)` with no interrupt:
  mkdir created `_cachedir` via `parents=True`
  set sees `_cachedir.exists()` true
  leftover: same omitted supporting-file identity as B, without a crash

Case D — `--cache-clear` then `set` on a missing dir:
  `clear_cache` removes the leftover dir
  not this leftover (fresh identity)

The developer wants to know which identity case B (and C) actually left for `.pytest_cache`: leftover "already initialized" dir (supporting files omitted), supporting-file identity present (`.gitignore` + `CACHEDIR.TAG`), or omitted (no cache dir at all).
""",
        observed="""# OBSERVED

Public pytest-dev/pytest#12167 (closed 2024-04-06). PR 12168 (tamird) merge `5acc3f86ac1713aea6775f04dcae35a2f0848437` (parents `4e3dd21506a9e543c04c63ebff966a9b604d2b9e` + `2e65f4e3ac81dd5e294839441262b8b112ba18bd`). Local pytest was not performed on this lab host.

Issue body: PR 3982's supporting-file write is gated on the cache directory not already existing. An interrupted cache write can leave `.pytest_cache` non-empty without `.gitignore`. The exists-already check then never creates `.gitignore`.

On failing_ref, `Cache.set` uses `path.parent.is_dir()` / `_cachedir.exists()` as the initialized-dir identity. `Cache.mkdir` does not call `_ensure_supporting_files`. `_ensure_supporting_files` is the only writer of `.gitignore` / `CACHEDIR.TAG` / `README.md`.

Atomic tempdir+rename of supporting files is **not** on the failing revision. It is added by PR 12168 (`_ensure_cache_dir_and_supporting_files`).

Not this packet: specimen-001 (assertion display evaluation order). specimen-002 (collection-identity / config-scope). specimen-003 (object-identity / fixture-closure). specimen-055 (derived rootdir collect). specimen-094 (vitest cache key). pytest#5702 / #3968 / #10002 / #14935 remain open (no merged fixed_ref).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# src/_pytest/cacheprovider.py Cache.set / Cache.mkdir / _ensure_supporting_files

# public shape:
# Cache.mkdir or interrupted Cache.set leaves .pytest_cache existing
# later Cache.set: cache_dir_exists_already True
# leftover: .gitignore / CACHEDIR.TAG omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""pytest-dev/pytest
  src/_pytest/cacheprovider.py
  changelog/12167.trivial.rst
""",
        source="""repository: pytest-dev/pytest
issue: https://github.com/pytest-dev/pytest/issues/12167
pr: https://github.com/pytest-dev/pytest/pull/12168
failing_ref (merge first parent): 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
fixed_ref (merge commit): 5acc3f86ac1713aea6775f04dcae35a2f0848437
second_parent: 2e65f4e3ac81dd5e294839441262b8b112ba18bd
merged_at: 2024-04-06T20:18:19Z
pr_author: tamird
merged_by: bluetech
changed_files: src/_pytest/cacheprovider.py, changelog/12167.trivial.rst, testing/test_assertrewrite.py
pr_title: Initialize cache directory in isolation
scout_note: not specimen-001/002/003. Distinct leftover: cache dir exists() identity omits supporting-file identity (.gitignore / CACHEDIR.TAG). job-0371 unique vs 001-003.
""",
        answer_key="""KNOWN FIX (sealed): pytest-dev/pytest PR 12168 merge 5acc3f86ac1713aea6775f04dcae35a2f0848437.

failing_ref is merge first parent 4e3dd21506a9e543c04c63ebff966a9b604d2b9e.

Cache.set treated leftover directory existence as initialized-cache identity and skipped supporting files. mkdir never wrote them.

PR repair: _ensure_cache_dir_and_supporting_files builds README/.gitignore/CACHEDIR.TAG in a TemporaryDirectory then rename onto _cachedir; early-return only if _cachedir.is_dir(); mkdir and set both go through _mkdir.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (first set writes supporting files vs leftover exists() omit vs mkdir-then-set omit vs --cache-clear)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — directory existence and supporting-file identity are different objects; leftover dir blocked .gitignore
ecosystem: python / pytest cache
mechanism_family: leftover-cache-dir, omitted-supporting-files, exists-gate

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "cacheprovider_set_failing.py": """# Reduced excerpt of Cache.set / mkdir / _ensure_supporting_files on failing_ref
# src/_pytest/cacheprovider.py
# 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# Directory existence is the initialized-cache identity.
# Supporting files are written only when that identity is absent.

    def mkdir(self, name: str) -> Path:
        path = Path(name)
        if len(path.parts) > 1:
            raise ValueError("name is not allowed to contain path separators")
        res = self._cachedir.joinpath(self._CACHE_PREFIX_DIRS, path)
        res.mkdir(exist_ok=True, parents=True)
        return res

    def set(self, key: str, value: object) -> None:
        path = self._getvaluepath(key)
        try:
            if path.parent.is_dir():
                cache_dir_exists_already = True
            else:
                cache_dir_exists_already = self._cachedir.exists()
                path.parent.mkdir(exist_ok=True, parents=True)
        except OSError as exc:
            self.warn(
                f"could not create cache path {path}: {exc}",
                _ispytest=True,
            )
            return
        if not cache_dir_exists_already:
            self._ensure_supporting_files()
        data = json.dumps(value, ensure_ascii=False, indent=2)
        try:
            f = path.open("w", encoding="UTF-8")
        except OSError as exc:
            self.warn(
                f"cache could not write path {path}: {exc}",
                _ispytest=True,
            )
        else:
            with f:
                f.write(data)

    def _ensure_supporting_files(self) -> None:
        readme_path = self._cachedir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="UTF-8")
        gitignore_path = self._cachedir.joinpath(".gitignore")
        msg = "# Created by pytest automatically.\\n*\\n"
        gitignore_path.write_text(msg, encoding="UTF-8")
        cachedir_tag_path = self._cachedir.joinpath("CACHEDIR.TAG")
        cachedir_tag_path.write_bytes(CACHEDIR_TAG_CONTENT)
""",
            "leftover_identity_split.txt": """Registry / fixture:
  cache_dir = .pytest_cache
  Cache.set / Cache.mkdir

Case A (first set, absent dir):
  supporting-file identity written
  no leftover uninitialized dir

Case B (interrupt after dir exists, no .gitignore):
  leftover: exists() identity
  .gitignore / CACHEDIR.TAG omitted

Case C (mkdir then set, no interrupt):
  mkdir created _cachedir via parents=True
  leftover: same omitted supporting files

Case D (--cache-clear then set):
  leftover dir removed
  not this leftover

Not this packet:
  assertion display evaluation order (specimen-001)
  collection-identity / config-scope (specimen-002)
  object-identity / fixture-closure (specimen-003)
  derived rootdir collect (specimen-055)
  vitest cache key (specimen-094)
  pytest#5702 / #3968 / #10002 / #14935 (open; no merged fixed_ref)
""",
        },
    )


def packet_npm(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: npm/cli
failing_ref: 696801574984ad19ffaa9a7200d7e752920a018d
fixed_ref: 981e2498589c83859b3c9e8b92a2cc67562dc06b
source_issue: https://github.com/npm/cli/issues/9613
source_pr: https://github.com/npm/cli/pull/9632
mechanism_tags:
  - leftover-bin-shim
  - linked-install-strategy
  - orphan-sweep-skips-dot-bin
ecosystem: npm
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7400
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Under npm `install-strategy=linked`, `npm uninstall <pkg>` can leave leftover **bin-shim identity** in `node_modules/.bin` after the package's top-level symlink and `.store` entry are gone. The leftover shim is a dangling link (POSIX) or a leftover `.cmd`/`.ps1` file (Windows). A later `npm install` does not heal it.

On failing_ref `696801574984ad19ffaa9a7200d7e752920a018d`, linked reify builds the actual tree for the diff from the ideal tree (`#buildLinkedActualForDiff`), so a removed dependency is never compared against disk and the diff emits no action to drop its bin shim. Post-reify `#cleanOrphanedStoreEntries` sweeps `.store` keys and top-level links. The top-level sweep **skips dot-entries**:

```
// skip npm-managed entries (.bin, .store, .package-lock.json, etc)
if (ent.name.startsWith('.')) {
    continue
}
```

There is no `#cleanStaleBinLinks`. `#cleanOrphanedStoreEntries` does not record `package.bin` names.

Public report (npm/cli#9613), `install-strategy=linked`:

```
package.json dependencies: rimraf@3.0.2, minimatch@3.0.4
npm install
ls node_modules/.bin                 # rimraf
npm uninstall rimraf
ls -l node_modules/.bin/rimraf
# node_modules/.bin/rimraf -> ../rimraf/bin.js   (dangling; ../rimraf gone)
```

Hoisted strategy removes the `.bin` entry.

In-tree after the repair (not on failing_ref): `t.test('removes stale .bin shims after uninstall, keeps surviving ones')` in `workspaces/arborist/test/arborist/reify.js`. Adds rimraf+semver linked, uninstalls rimraf, expects rimraf / rimraf.cmd / rimraf.ps1 gone and semver shims kept.

Case A — hoisted `npm uninstall rimraf` (no linked):
  diff sees the on-disk tree
  `.bin/rimraf` removed
  no leftover shim identity

Case B — linked `npm uninstall rimraf` while `semver` remains:
  top-level `rimraf` symlink and `.store` entry removed
  leftover: `.bin/rimraf` (and `.cmd`/`.ps1`) still named rimraf
  surviving `.bin/semver` should stay

Case C — linked first install (never installed rimraf):
  no leftover uninstall shim
  not this leftover

Case D — linked uninstall then `rm -rf node_modules && npm install`:
  fresh tree
  not leftover identity (wipe, not sweep)

The developer wants to know which identity case B actually left in `node_modules/.bin`: leftover rimraf shim (dangling / stale name), both shims removed, or omitted (no `.bin` directory).
""",
        observed="""# OBSERVED

Public npm/cli#9613 (closed 2026-06-24). PR 9632 merge `981e2498589c83859b3c9e8b92a2cc67562dc06b` (single parent / squash `696801574984ad19ffaa9a7200d7e752920a018d`). Part of #9608 linked-strategy leftovers. Local npm was not performed on this lab host.

PR body: under linked, uninstall removed the top-level symlink and `.store` entry but left the shim in `node_modules/.bin` as a dangling link. The leftover shim can break tools that enumerate `.bin`, shadow a later-installed binary of the same name, and is not healed by a subsequent `npm install`. Hoisted removes the `.bin` entry.

On failing_ref, `#cleanOrphanedStoreEntries` collects valid store keys and valid top-level link names, then `#cleanOrphanedTopLevelLinks` removes orphaned symlinks whose names do not start with `.`. `.bin` is skipped as an npm-managed dot-entry. No `binsByDir` / `#cleanStaleBinLinks`.

`#cleanStaleBinLinks` is **not** on the failing revision. It is added by PR 9632: while collecting valid top-level links, record `child.package.bin` names per `node_modules` dir; then remove `.bin` entries whose base name (after stripping `.cmd`/`.ps1`) is not provided by a surviving package, or which are dangling symlinks.

Not this packet: specimen-004 / specimen-033 (npm optional-peer leftover). specimen-082 (bun optional-peer leftover / Honor-KILL peerleft). specimen-095 (npm nested-override leftover / Honor-KILL overleft). specimen-089 (yarn leftover PnP build state). job-0394/0419 npm peer leftover (duplicate 004/082/095).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 696801574984ad19ffaa9a7200d7e752920a018d
# workspaces/arborist/lib/arborist/reify.js #cleanOrphanedStoreEntries
# workspaces/arborist/test/arborist/reify.js linked stale .bin test (on the PR, not failing_ref)

# public shape (linked):
# npm uninstall rimraf
# leftover: node_modules/.bin/rimraf -> ../rimraf/bin.js (dangling)
# store entry and top-level symlink gone
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""npm/cli
  workspaces/arborist/lib/arborist/reify.js
  workspaces/arborist/test/arborist/reify.js
""",
        source="""repository: npm/cli
issue: https://github.com/npm/cli/issues/9613
pr: https://github.com/npm/cli/pull/9632
failing_ref (squash parent): 696801574984ad19ffaa9a7200d7e752920a018d
fixed_ref (squash merge): 981e2498589c83859b3c9e8b92a2cc67562dc06b
merged_at: 2026-06-24T18:17:22Z
changed_files: workspaces/arborist/lib/arborist/reify.js, workspaces/arborist/test/arborist/reify.js
pr_title: fix(arborist): remove stale .bin shims after uninstall under linked
scout_note: not specimen-004/082/095 peer leftover. Distinct leftover: linked uninstall sweeps store+top-level links but skips .bin, leaving dangling shim identity. job-0339 git+ssh vs registry had no merged pair; packed this leftover-identity instead.
""",
        answer_key="""KNOWN FIX (sealed): npm/cli PR 9632 squash 981e2498589c83859b3c9e8b92a2cc67562dc06b.

failing_ref is squash parent 696801574984ad19ffaa9a7200d7e752920a018d.

Linked uninstall's actual-tree diff never emitted a drop for the bin shim. #cleanOrphanedStoreEntries skipped .bin as a dot-entry. Leftover rimraf shim identity remained after store+top-level cleanup.

PR repair: binsByDir from still-linked package.bin; #cleanStaleBinLinks removes .bin names not provided by survivors (and dangling symlinks), keeping surviving shims including Windows .cmd/.ps1.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (hoisted uninstall drops shim vs linked leftover dangling shim vs first install vs wipe+reinstall)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — store/top-level link identity and .bin shim identity are different objects; linked diff never saw the leftover shim
ecosystem: npm / arborist linked
mechanism_family: leftover-bin-shim, linked-strategy, omitted-dot-sweep

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "reify_clean_orphaned_failing.js": """// Reduced excerpt of #cleanOrphanedStoreEntries / top-level sweep on failing_ref
// workspaces/arborist/lib/arborist/reify.js
// 696801574984ad19ffaa9a7200d7e752920a018d
// Store keys and top-level links are swept. .bin is skipped as a dot-entry.
// No binsByDir / #cleanStaleBinLinks.

  async #cleanOrphanedStoreEntries () {
    const nmDir = resolve(this.path, 'node_modules')
    const storeDir = resolve(nmDir, '.store')
    const validKeys = new Set()
    const nmDirs = new Map()
    // ... collect valid store keys and top-level link names from idealTree ...
    for (const [dir, valid] of nmDirs) {
      await this.#cleanOrphanedTopLevelLinks(dir, valid)
    }
  }

    const orphaned = []
    for (const ent of dirents) {
      // skip npm-managed entries (.bin, .store, .package-lock.json, etc)
      if (ent.name.startsWith('.')) {
        continue
      }
      // ... orphaned top-level symlink sweep ...
    }
""",
            "leftover_identity_split.txt": """Registry / fixture:
  install-strategy=linked
  deps: rimraf + semver (or minimatch)
  npm uninstall rimraf

Case A (hoisted uninstall):
  .bin/rimraf removed
  no leftover shim

Case B (linked uninstall, semver remains):
  leftover: .bin/rimraf dangling
  store + top-level rimraf gone
  .bin/semver kept

Case C (linked first install, rimraf never present):
  no leftover uninstall shim

Case D (rm -rf node_modules && npm install):
  fresh tree
  not leftover sweep

Not this packet:
  npm optional-peer leftover (specimen-004/033)
  bun optional-peer leftover (specimen-082)
  npm nested-override leftover (specimen-095)
  yarn leftover PnP build state (specimen-089)
  cargo git+ssh vs registry (job-0339: no merged PR)
""",
        },
    )


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        raise SystemExit(f"{job_id} missing")
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
            raise SystemExit(
                f"{job_id} status=CLAIMED worker={old}"
            )
        job["worker"] = worker
        job["claimed_at"] = job.get("claimed_at") or now_jst()
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
        for w in workers:
            if w.get("id") != worker and w.get("job") == job_id:
                w["status"] = "vacant"
                w["job"] = None
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(
            f"{job_id} status={job.get('status')} worker={job.get('worker')}"
        )


def _register(state, spec_id: str, trial: str, reason: str) -> None:
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
            input_ref=f"seeds/{spec_id}.md trial={trial}",
            expected_output="0001-dreamer.md",
            kill_condition="15m",
            estimated_cost="r1",
            priority_reason=reason,
            specimen=spec_id,
            lineage=trial,
            phase="cambrian",
            extra={"trial": trial},
        )


def _complete_and_enqueue(py_id: str, npm_id: str) -> str:
    note = {"reason": ""}

    def fn(state):
        _claim_job(state, JOB_PY, WORKER_PY)
        _claim_job(state, JOB_NPM, WORKER_NPM)
        job_py = next(j for j in state["ready_jobs"] if j["id"] == JOB_PY)
        job_npm = next(j for j in state["ready_jobs"] if j["id"] == JOB_NPM)
        if job_py.get("status") == "CLAIMED" and job_py.get("worker") == WORKER_PY:
            complete(
                state,
                JOB_PY,
                result="skip",
                artifact=(
                    "skip hatch dist cache leftover vs pyproject: hatch#2345/"
                    "PR 2351 is leftover CLI plugin-manager identity not dist "
                    f"cache; packed leftover cache-dir as {py_id} instead"
                ),
            )
        if job_npm.get("status") == "CLAIMED" and job_npm.get("worker") == WORKER_NPM:
            complete(
                state,
                JOB_NPM,
                result="skip",
                artifact=(
                    "skip cargo git+ssh vs registry leftover: cargo#14526 "
                    "closed without merged PR; #14466/#10756 not_planned; "
                    "#13549 is SSH URL error-message (PR 15185). Packed npm "
                    f"leftover .bin shim leftover-identity as {npm_id} instead"
                ),
            )
        _register(
            state,
            py_id,
            TRIAL_PY,
            "pytest leftover cache-dir identity omits gitignore; not 001-003",
        )
        _register(
            state,
            npm_id,
            TRIAL_NPM,
            "npm linked leftover .bin shim identity; not 004/082/095 peer leftover",
        )
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") == "READY":
                job["status"] = "CLAIMED"
                job["worker"] = WORKER_PY
                job["claimed_at"] = now_jst()
                complete(state, jid, result="skip", artifact=artifact)
        claimed_r1 = [
            j
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_R1_DREAM" and j.get("status") == "CLAIMED"
        ]
        if claimed_r1:
            note["reason"] = (
                "dream.sh not launched; READY_R1_DREAM already in flight: "
                + ",".join(f"{j['id']}:{j.get('lineage')}" for j in claimed_r1)
            )
        else:
            note["reason"] = (
                "dream.sh not launched from scout; READY_R1_DREAM enqueued "
                f"trials={TRIAL_PY},{TRIAL_NPM}"
            )
        return (py_id, npm_id)

    with_state(fn)
    return note["reason"]


def main() -> None:
    py_id = _claim_id()
    npm_id = _claim_id()
    py_dest = SPECIMENS / py_id
    npm_dest = SPECIMENS / npm_id
    try:
        p1 = emit(packet_pytest(py_id))
        s1 = write_seed(SPECIMENS / py_id)
        p2 = emit(packet_npm(npm_id))
        s2 = write_seed(SPECIMENS / npm_id)
        update_index()
        launch_note = _complete_and_enqueue(py_id, npm_id)
        print(p1)
        print(s1)
        print(p2)
        print(s2)
        print(launch_note)
        print(f"ids={py_id},{npm_id} trials={TRIAL_PY},{TRIAL_NPM}")
    except Exception:
        for dest in (py_dest, npm_dest):
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
