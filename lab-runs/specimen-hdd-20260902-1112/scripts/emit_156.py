#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 156+.

Packed (unique vs 001-155; 075 not overwritten; not bazel#29298):
1) microsoft/vcpkg-tool#1997 (follow-up of #1988):
   leftover unset identity after Windows GetEnvironmentVariableW(sz==0)
   JOIN of empty FOO= and unset FOO. Empty string, unset, and a present
   value are different identities.
2) gleam-lang/gleam#4320 / PR 4325:
   leftover compile cache of module `a` after the source was moved out
   then restored, because removed modules were only marked stale and
   cache files were not deleted. Same-name source vs leftover cache.

SKIP claimed job-0666 (rebar leftover compile vs source: no merged
leftover-identity pair this tick; mix 154 is elixir digest, not rebar).
Do not pack leftover-flag omitted-flush/cache-line TSV (ansflush/skafdig
class; 105-141 leftover-flag batch; hexcksum/mixdigest/clangdmod omitted
key). Distinct from packed 001-155. Never overwrite 075.
"""
from __future__ import annotations

import os
import subprocess

from compile_seed import write_seed
from emit_specimen import emit
from paths import HDD_ROOT, RUN_DIR, SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 156
WORKER = "scout-leftover-2155"
SKIP_JOBS = {
    "job-0666": (
        "skip rebar leftover compile vs source identity: no merged leftover-"
        "HIT omitted-digest pair this tick (recent rebar3 merges are CI bumps). "
        "not inventing refs; not 054/154/155"
    ),
}
NEXT_SCOUTS = [
    (
        "public OSS: php leftover opcache vs replaced file identity not 110",
        "unique php opcache leftover if pinned",
    ),
    (
        "public OSS: node leftover compile cache vs source identity not 082/090",
        "unique node compile-cache leftover if pinned",
    ),
    (
        "public OSS: crystal leftover compile vs moved module identity not 054/154",
        "unique crystal leftover if pinned",
    ),
    (
        "public OSS: nim leftover cache vs moved module identity not 054",
        "unique nim leftover if pinned",
    ),
    (
        "public OSS: lua leftover package.loaded vs moved file identity not 054",
        "unique lua leftover if pinned",
    ),
    (
        "public OSS: perl leftover INC vs moved file identity not 054",
        "unique perl leftover if pinned",
    ),
    (
        "public OSS: julia leftover precompile vs moved module identity not 054",
        "unique julia leftover if pinned",
    ),
    (
        "public OSS: haskell leftover hi vs moved module identity not 054",
        "unique haskell leftover if pinned",
    ),
    (
        "public OSS: ocaml leftover cmi vs moved module identity not 054",
        "unique ocaml leftover if pinned",
    ),
    (
        "public OSS: javac leftover classfile vs moved source identity not 096",
        "unique javac leftover if pinned",
    ),
    (
        "public OSS: kotlin leftover incremental vs moved file identity not 104",
        "unique kotlin leftover if pinned",
    ),
    (
        "public OSS: swift leftover modulecache vs moved file identity not 121",
        "unique swift leftover if pinned",
    ),
    (
        "public OSS: dart leftover kernel vs moved file identity not 128",
        "unique dart leftover if pinned",
    ),
    (
        "public OSS: direnv leftover empty vs unset JOIN identity not 010/149/150/156",
        "unique direnv empty-vs-unset if pinned",
    ),
    (
        "public OSS: github-actions leftover empty vs unset env identity not 010/149/156",
        "unique actions empty-vs-unset if pinned",
    ),
    (
        "public OSS: nginx leftover empty vs unset JOIN identity not 010/149/150",
        "unique nginx empty-vs-unset if pinned",
    ),
    (
        "public OSS: envoy leftover empty vs unset JOIN identity not 010/149/150",
        "unique envoy empty-vs-unset if pinned",
    ),
    (
        "public OSS: go leftover object vs moved file identity not 075/103",
        "unique go leftover object if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 190):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_vcpkg(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: microsoft/vcpkg-tool
failing_ref: e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
fixed_ref: 643c71f3626a7820e48c51d11545711a594dad02
source_issue: https://github.com/microsoft/vcpkg-tool/pull/1997
source_pr: https://github.com/microsoft/vcpkg-tool/pull/1997
mechanism_tags:
  - leftover-empty-vs-unset
  - getenv-zero-join
  - windows-empty-env
ecosystem: vcpkg
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

vcpkg `get_environment_variable` on Windows can keep the identity of **unset** after the process listed `FOO=` (equals, empty string) and that listing should have meant present-and-empty. `GetEnvironmentVariableW` returns size `0` for both ERROR_ENVVAR_NOT_FOUND and a present empty value. The JOIN of empty and unset is one leftover identity.

On failing_ref `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`:

```
Optional<std::string> get_environment_variable(ZStringView varname)
{
#if defined(_WIN32)
    const auto w_varname = Strings::to_utf16(varname);
    const auto sz = GetEnvironmentVariableW(w_varname.c_str(), nullptr, 0);
    if (sz == 0) return nullopt;

    std::wstring ret(sz, L'\\0');
    Checks::check_exit(VCPKG_LINE_INFO, MAXDWORD >= ret.size());
    const auto sz2 = GetEnvironmentVariableW(w_varname.c_str(), ret.data(), static_cast<DWORD>(ret.size()));
    Checks::check_exit(VCPKG_LINE_INFO, sz2 + 1 == sz);
    ret.pop_back();
    return Strings::to_utf8(ret.c_str());
#else
    auto v = getenv(varname.c_str());
    if (!v) return nullopt;
    return std::string(v);
#endif
}
```

`sz == 0` is the JOIN. Unset is `nullopt`. Empty `FOO=` is also `nullopt`. A present `FOO=bar` is a string. POSIX `getenv` already splits NULL vs `""`; the Windows size-zero probe does not.

Public report (microsoft/vcpkg-tool#1997), follow-up of #1988 (`HTTPS_PROXY` / `NO_PROXY` empty vs unset). Tests after the repair: unset → no value; `FOO=` → has_value and empty string; `FOO=x` → `x`. Callers that want empty-as-absent use a separate helper after the repair.

In-tree after the repair (not on failing_ref): `SetLastError(ERROR_SUCCESS)` then `GetEnvironmentVariableW` into an SSO buffer; `sz == 0` with `ERROR_ENVVAR_NOT_FOUND` is unset; `sz == 0` with `ERROR_SUCCESS` is empty present.

Case A — `FOO` unset (`ERROR_ENVVAR_NOT_FOUND`):
  unset identity
  not leftover-empty-as-unset

Case B — `FOO=` empty string, leftover JOIN:
  leftover: unset / `nullopt`
  Windows size-zero probe
  same process lookup

Case C — `FOO=bar` present:
  current string identity
  not leftover unset

Case D — empty present kept (post-repair shape, not on failing_ref):
  has_value empty string
  not leftover unset

The developer wants to know which identity case B actually used for `FOO` after listing `FOO=`: leftover unset (`sz==0` JOIN), current empty string, or omitted (no getenv).
""",
        observed="""# OBSERVED

Public microsoft/vcpkg-tool#1997 (merged 2026-05-12). Squash `643c71f3626a7820e48c51d11545711a594dad02` (parent `e03454a3cffaafbbe5235078b6f2c5bf13ea32bc`). Follow-up of #1988 (empty HTTPS_PROXY / NO_PROXY treated as unset). Local vcpkg-tool was not performed on this lab host.

PR title: Fix empty vs. unset environment variables on Windows. Same defect as #1988 on the normal getenv path. Audit callers.

On failing_ref, Windows `GetEnvironmentVariableW(..., nullptr, 0)` returning 0 is treated as unset. Empty `FOO=` and unset FOO JOIN. POSIX getenv already distinguishes NULL vs empty.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global. specimen-149 compose listed-without-equals vs image ENV. specimen-150 systemd `::` cwd search path.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
# src/vcpkg/base/system.cpp get_environment_variable

# public shape:
# leftover unset after FOO= empty on Windows
# GetEnvironmentVariableW sz==0 JOINs empty and unset
# FOO=bar is a present string; POSIX getenv already splits
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""microsoft/vcpkg-tool
  src/vcpkg/base/system.cpp
  src/vcpkg-test/system.cpp
  include/vcpkg/base/system.h
""",
        source="""repository: microsoft/vcpkg-tool
issue: https://github.com/microsoft/vcpkg-tool/pull/1997
pr: https://github.com/microsoft/vcpkg-tool/pull/1997
related_pr: https://github.com/microsoft/vcpkg-tool/pull/1988
failing_ref (parent of squash on main): e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
fixed_ref (Windows empty vs unset split): 643c71f3626a7820e48c51d11545711a594dad02
merged_at: 2026-05-12T20:12:07Z
pr_author: BillyONeal
merged_by: BillyONeal
changed_files: include/vcpkg/base/system.h, src/vcpkg/base/system.cpp, src/vcpkg-test/system.cpp, src/vcpkg/binarycaching.cpp, src/vcpkg/commands.build.cpp, src/vcpkg/commands.edit.cpp, src/vcpkg/commands.integrate.cpp, src/vcpkg/vcpkgcmdarguments.cpp, src/vcpkg/visualstudio.cpp, src/vcpkg-test/util.cpp
pr_title: Fix empty vs. unset environment variables on Windows.
scout_note: not 010/031/149/150. leftover unset after empty FOO= JOIN on Windows GetEnvironmentVariableW sz==0. unique vs 001-155.
""",
        answer_key="""KNOWN FIX (sealed): microsoft/vcpkg-tool PR 1997 squash 643c71f3626a7820e48c51d11545711a594dad02.

failing_ref is parent e03454a3cffaafbbe5235078b6f2c5bf13ea32bc.

Windows get_environment_variable treated GetEnvironmentVariableW size 0 as unset. Empty FOO= and unset FOO JOIN to leftover nullopt.

PR repair: distinguish ERROR_ENVVAR_NOT_FOUND from ERROR_SUCCESS empty; callers that want empty-as-absent use get_environment_variable_nonempty.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unset vs leftover unset after FOO= JOIN vs present FOO=bar vs empty present)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — empty string and unset JOIN to one Windows size-zero identity; two greps cannot replace
ecosystem: vcpkg / Windows getenv
mechanism_family: leftover-empty-vs-unset, getenv-zero-join, windows-empty-env

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "getenv_failing.cpp": """// Reduced excerpt of get_environment_variable on failing_ref
// src/vcpkg/base/system.cpp
// e03454a3cffaafbbe5235078b6f2c5bf13ea32bc
// Windows size-zero probe JOINs empty FOO= and unset FOO into leftover nullopt.

Optional<std::string> get_environment_variable(ZStringView varname)
{
#if defined(_WIN32)
    const auto w_varname = Strings::to_utf16(varname);
    const auto sz = GetEnvironmentVariableW(w_varname.c_str(), nullptr, 0);
    if (sz == 0) return nullopt;
    std::wstring ret(sz, L'\\0');
    const auto sz2 = GetEnvironmentVariableW(w_varname.c_str(), ret.data(), static_cast<DWORD>(ret.size()));
    Checks::check_exit(VCPKG_LINE_INFO, sz2 + 1 == sz);
    ret.pop_back();
    return Strings::to_utf8(ret.c_str());
#else
    auto v = getenv(varname.c_str());
    if (!v) return nullopt;
    return std::string(v);
#endif
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  vcpkg get_environment_variable Windows
  leftover unset after empty FOO= JOIN

Case A (FOO unset):
  unset identity
  not leftover-empty-as-unset

Case B (FOO= empty string, leftover JOIN):
  leftover: unset / nullopt
  GetEnvironmentVariableW sz==0

Case C (FOO=bar present):
  current string identity
  not leftover unset

Case D (empty present kept):
  has_value empty string
  not leftover unset

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  compose listed-without-equals vs image ENV (specimen-149)
  systemd empty :: cwd search path (specimen-150)
""",
        },
    )


def packet_gleam(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: gleam-lang/gleam
failing_ref: 3767575d05372e4b823c132afacb28e52fbe3aa1
fixed_ref: b3e1ceb15118c3b4abb0909ef1f2baca6abacd37
source_issue: https://github.com/gleam-lang/gleam/issues/4320
source_pr: https://github.com/gleam-lang/gleam/pull/4325
mechanism_tags:
  - leftover-compile-cache
  - same-name-module-after-move
  - cache-vs-source-identity
ecosystem: gleam
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Gleam `PackageLoader` can keep the identity of a **previous compile cache** for module `a` after `a.gleam` was moved out of `src` and later restored, and that cache should not have been current. Removed modules are added to a stale tracker. Cache files stay. Restoring the same-name source with the same bytes takes the leftover previous cache even after dependency `b` changed.

On failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`:

```
// Check for any removed modules, by looking at cache files that don't exist in inputs
for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if (!inputs.contains_key(&module)) {
        self.stale_modules.add(module);
    }
}
```

`ModuleLoader::load` uses leftover cache when source fingerprint matches:

```
if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))
```

Stale-deps load deletes `cache_meta` only. Removed-module cache files are not deleted. Same-name restored source and leftover cache JOIN.

Public report (gleam-lang/gleam#4320). Add `a.gleam` that calls `b.f`; build; move `a` out; change `b.f`; build; restore `a` unchanged; build. Expected: compile error on the new `b.f`. Actual: leftover previous `a` cache, runtime "function did not exist".

In-tree after the repair (not on failing_ref): cache files are deleted when the source is gone; restoring `a` is a new compile.

Case A — second build, `a.gleam` never left, `b` unchanged:
  cache identity is current
  not leftover-after-move

Case B — `a` moved out then restored, leftover cache:
  leftover: previous compile of `a` (old `b.f`)
  same-name source vs leftover cache files
  `b` already changed

Case C — `gleam clean` / no artefact cache:
  fresh compile of restored `a`
  not leftover previous cache

Case D — cache files deleted on source removal (post-repair shape, not on failing_ref):
  new compile after restore
  not leftover previous `a`

The developer wants to know which identity case B actually used for module `a` after the restore: leftover previous-cache (same-name files stayed), current source vs new `b`, or omitted (no cache).
""",
        observed="""# OBSERVED

Public gleam-lang/gleam#4320 (closed 2025-03-20). PR 4325 rebase-merge last commit `b3e1ceb15118c3b4abb0909ef1f2baca6abacd37` (first PR commit on main `588caed189988e96ff51f5e209c4d35151a396cd`, parent `3767575d05372e4b823c132afacb28e52fbe3aa1`). Local gleam was not performed on this lab host.

Issue body: temporarily removed file does not always get recompiled. Cache files of missing sources are not deleted. mtime is not enough when restored content matches the leftover fingerprint. Follow-on of #3873 (mark removed modules stale without deleting cache).

On failing_ref, `PackageLoader::run` adds missing cache modules to `stale_modules`. `ModuleLoader::load` returns `Input::Cached` when fingerprint matches. Restored same-name `a.gleam` JOINs with leftover cache.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-155 clangd leftover BMI.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 3767575d05372e4b823c132afacb28e52fbe3aa1
# compiler-core/src/build/package_loader.rs removed-module loop
# compiler-core/src/build/module_loader.rs fingerprint cache hit

# public shape:
# leftover compile cache of a after a.gleam moved out then restored
# stale tracker add without deleting cache files
# gleam clean / miss writes a new compile
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""gleam-lang/gleam
  compiler-core/src/build/package_loader.rs
  compiler-core/src/build/module_loader.rs
  compiler-core/src/build/package_loader/tests.rs
""",
        source="""repository: gleam-lang/gleam
issue: https://github.com/gleam-lang/gleam/issues/4320
pr: https://github.com/gleam-lang/gleam/pull/4325
failing_ref (parent of first rebased PR commit on main): 3767575d05372e4b823c132afacb28e52fbe3aa1
fixed_ref (rebase-merge last commit, cache files deleted on source removal): b3e1ceb15118c3b4abb0909ef1f2baca6abacd37
merged_at: 2025-03-20T12:46:13Z
pr_author: sbergen
merged_by: lpil
changed_files: compiler-core/src/build/package_loader.rs, compiler-core/src/build/module_loader.rs, compiler-core/src/build/package_loader/tests.rs, compiler-core/src/build/module_loader/tests.rs, compiler-core/src/build.rs, compiler-core/src/codegen.rs, compiler-core/src/erlang.rs, compiler-core/src/io.rs, CHANGELOG.md
pr_title: Fix and clarify cache file handling
scout_note: not 054/154/155. leftover same-name gleam cache after source moved out then restored. unique vs 001-155.
""",
        answer_key="""KNOWN FIX (sealed): gleam-lang/gleam PR 4325 rebase-merge b3e1ceb15118c3b4abb0909ef1f2baca6abacd37.

failing_ref is parent of first rebased PR commit: 3767575d05372e4b823c132afacb28e52fbe3aa1.

Removed modules were marked stale; cache files stayed. Restored same-name source with matching fingerprint took leftover previous compile of `a` after `b` changed.

PR repair: delete cache files when the source is gone; restoring `a` is a new compile.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (never-moved current cache vs leftover cache after move+restore vs clean vs deleted-on-remove)
reproducibility: source-backed issue+PR + pinned parent/rebase-merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — same-name restored source and leftover cache JOIN; two greps cannot replace
ecosystem: gleam / compile cache
mechanism_family: leftover-compile-cache, same-name-module-after-move, cache-vs-source-identity

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "package_loader_failing.rs": """// Reduced excerpt of PackageLoader::run on failing_ref
// compiler-core/src/build/package_loader.rs
// 3767575d05372e4b823c132afacb28e52fbe3aa1
// removed modules are marked stale; cache files stay.

for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if !inputs.contains_key(&module) {
        self.stale_modules.add(module);
    }
}
""",
            "module_loader_failing.rs": """// Reduced excerpt of ModuleLoader::load on failing_ref
// compiler-core/src/build/module_loader.rs
// leftover cache HIT when restored source fingerprint matches.

if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))
""",
            "leftover_identity_split.txt": """Registry / fixture:
  gleam PackageLoader / ModuleLoader
  leftover compile cache of a after a.gleam moved out then restored

Case A (a never left, b unchanged):
  current cache identity
  not leftover-after-move

Case B (a moved out then restored, leftover cache):
  leftover: previous compile of a (old b.f)
  same-name source vs leftover cache files

Case C (gleam clean / no artefact cache):
  fresh compile of restored a
  not leftover previous cache

Case D (cache files deleted on source removal):
  new compile after restore
  not leftover previous a

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  clangd leftover BMI (specimen-155)
""",
        },
    )


PACKETS = [
    (None, "hdd-vcpkgenv", packet_vcpkg,
     "vcpkg leftover unset after empty FOO= Windows sz==0 JOIN; not 010/149/150"),
    (None, "hdd-gleamrm", packet_gleam,
     "gleam leftover same-name cache after source moved then restored; not 054/154/155"),
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
