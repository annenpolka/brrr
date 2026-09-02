#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet (yarn leftover PnP build identity).

yarnpkg/berry#2452 / PR 2801. Leftover storedBuildState after .yarn/unplugged
is removed vs never-built first install. Not specimen-082 / Honor-KILL peerleft
(bun.lock packages row vs optionalPeers mention). Not #1490 leftover
dependenciesMeta.unplugged after yarn remove (open, no fixed_ref). Not
specimen-087 leftover pnpm patchedDependencies path field.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, with_state
from update_index import main as update_index

JOB_ID = "job-0318"
WORKER = "scout-yarn-pnp"
TRIAL = "hdd-pnpstale"
FORBIDDEN = {f"specimen-{n:03d}" for n in range(75, 89)}
START_N = 89


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 100):
        spec_id = f"specimen-{n:03d}"
        if spec_id in FORBIDDEN:
            continue
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id in 089-099")


def packet_for(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: yarnpkg/berry
failing_ref: 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
fixed_ref: a2ea850802f3d05129edb179d902890744c03e65
source_issue: https://github.com/yarnpkg/berry/issues/2452
source_pr: https://github.com/yarnpkg/berry/pull/2801
mechanism_tags:
  - leftover-build-state
  - unplugged-folder-remove
  - pnp-packageLocation-path-hash
ecosystem: yarn-pnp
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Yarn PnP unplugs packages that have install scripts. After the unplugged tree is deleted, a later `yarn install` does not return the locator to the identity it had before that package was ever built.

Fixture `no-deps-scripted` (has an install script). Public report used `@sentry/cli@1.62.0` (install script downloads a native binary).

Case A — never built (first install, empty `storedBuildState`):

```
package.json: { "dependencies": { "no-deps-scripted": "*" } }
yarn install
```

On yarnpkg/berry `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`, stdout contains `YN0007` (`MUST_BUILD`: "must be built because it never has been before or the last one failed"). PnP writes `packageLocation` under `.yarn/unplugged/no-deps-scripted-npm-…/`. `Project.storedBuildState` then maps that locatorHash to a sha512 `buildHash`. A `.ready` file appears inside the unplugged prefix.

Case B — second install, unplugged tree still present:

```
yarn install
```

stdout does **not** contain `YN0007`. `storedBuildState.get(locatorHash) === buildHash`, so scripts are skipped. PnP `packageLocation` is still the unplugged path.

Case C — remove the unplugged tree, then install again (package remains in `package.json`; this is not `yarn remove no-deps-scripted`):

```
rm -rf .yarn/unplugged
yarn install
```

`PnpInstaller.unplugPackage` sees no `.ready` file, recopies the zip into `.yarn/unplugged/…`, and writes `.ready` again. `getBuildHash` is sha512 of `globalHash + getBaseHash(locator) + buildLocation path strings`. Those path strings are the same unplugged paths as case A, so `buildHash` is unchanged. On the failing revision `storedBuildState` still holds that hash, so the skip in case B fires: no `YN0007`, install scripts do not run.

Public `@sentry/cli@1.62.0` observable after case C:

```
yarn sentry-cli --version
# Error: spawn /.yarn/unplugged/@sentry-cli-npm-1.62.0-…/node_modules/@sentry/cli/sentry-cli ENOENT
```

PnP `packageLocation` still names the unplugged directory (same as a successful first build). `storedBuildState` still names the locator as already-built. The native binary is absent.

Case D — never installed `no-deps-scripted` at all: no PnP registry entry for that ident, no `storedBuildState` row, no `.yarn/unplugged/no-deps-scripted-*` directory.

The developer wants to know which identity install-state + PnP actually contained for the locator after case C: leftover already-built `buildHash` (scripts skipped, same skip as case B), omitted (same `YN0007` as case A / never-built), or a new hash because the unplugged files were gone.
""",
        observed="""# OBSERVED

Public yarnpkg/berry#2452 (mzvonar, 2021-02-08) / PR 2801. Failing world: Yarn 2.4.0 and commit `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`.

Issue reproduction:

```
yarn init
yarn set version berry
yarn add @sentry/cli@1.62.0
rm -rf .yarn/unplugged
yarn install
yarn sentry-cli --version
```

Expected after the second install: install scripts run again; `sentry-cli` binary exists under the unplugged prefix.

Saw: scripts skipped; `spawn …/sentry-cli ENOENT`. Collaborator note: "The info containing what has been built is located in `.yarn/build-state.yml` (for now)" — on this revision that map is `Project.storedBuildState` inside install-state (`INSTALL_STATE_FIELDS.restoreBuildState`). Workaround quoted in the issue: `rm -rf .yarn/unplugged .yarn/build-state.yml && yarn`, or `yarn rebuild`.

In-tree skip on the failing revision (`packages/yarnpkg-core/sources/Project.ts`):

```
const buildHash = getBuildHash(pkg, buildInfo.buildLocations);
if (this.storedBuildState.get(pkg.locatorHash) === buildHash) {
  nextBState.set(pkg.locatorHash, buildHash);
  continue;
}
if (this.storedBuildState.has(pkg.locatorHash))
  report.reportInfo(MessageName.MUST_REBUILD, `… must be rebuilt because its dependency tree changed`);
else
  report.reportInfo(MessageName.MUST_BUILD, `… must be built because it never has been before or the last one failed`);
```

`MUST_BUILD` is `MessageName` 7 → `YN0007`. `getBuildHash` updates sha512 with `globalHash`, `getBaseHash(locator)`, then each `buildLocations` **path string**. It does not hash unplugged file contents. Comment immediately above the rebuild loop: "We reconstruct the build state from an empty object because we want to remove the state from packages that got removed" — that prune is for locators that left `buildablePackages` (`yarn remove` of the package). Case C keeps the locator in the tree.

`PnpInstaller.unplugPackage` on the failing revision (`packages/plugin-pnp/sources/PnpLinker.ts`):

```
const readyFile = ppath.join(unplugPath, fetchResult.prefixPath, `.ready`);
if (await xfs.existsPromise(readyFile))
  return new CwdFS(unplugPath);
await xfs.mkdirPromise(unplugPath, {recursive: true});
await xfs.copyPromise(unplugPath, PortablePath.dot, {baseFs: fetchResult.packageFs, overwrite: false});
await xfs.writeFilePromise(readyFile, ``);
```

No `storedBuildState.delete`. After `rm -rf .yarn/unplugged`, `.ready` is gone so the zip is recopied, but the leftover hash still matches.

PR 2801 later added `pnp.test.js` "it should run the install scripts anew if the unplugged folder is removed" (`no-deps-scripted`): first install `YN0007`, second install no `YN0007`, `rm` unplugged, third install expects `YN0007`. That third assertion is the case-C identity. The test file on the failing revision does not yet contain that case.

Unused-unplugged **directories** for packages that left the tree are already deleted in `finalizeInstallWithPnp` (`unpluggedPaths` set). This packet is not that prune, not bun leftover `packages` vs `optionalPeers` mention, and not leftover `dependenciesMeta.unplugged` after `yarn remove` (#1490, still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""# COMMANDS

```
# in-tree on failing_ref 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
# (not executed on this lab host)

# case A — never built
# package.json dependencies: no-deps-scripted: *
yarn install
# stdout contains YN0007 MUST_BUILD
# .pnp.cjs packageLocation under .yarn/unplugged/no-deps-scripted-npm-*/
# storedBuildState now has locatorHash → sha512 buildHash
# unplugged prefix contains .ready

# case B — leftover already-built, tree still present
yarn install
# stdout does not contain YN0007
# storedBuildState.get(locatorHash) === getBuildHash(pkg, buildLocations)

# case C — remove unplugged tree; package still in package.json
rm -rf .yarn/unplugged
yarn install
# unplugPackage recopies zip (no .ready)
# getBuildHash still hashes the same unplugged path strings
# leftover storedBuildState matches → no YN0007; scripts skipped

# public #2452
# yarn add @sentry/cli@1.62.0
# rm -rf .yarn/unplugged && yarn install
# yarn sentry-cli --version
# spawn …/.yarn/unplugged/@sentry-cli-npm-1.62.0-…/sentry-cli ENOENT

# case D — never installed
# no PnP registry ident, no storedBuildState row, no unplugged directory
```

Not executed on this lab host.
""",
        tree="""yarnpkg/berry
  packages/plugin-pnp/sources/PnpLinker.ts
  packages/yarnpkg-core/sources/Project.ts
  packages/yarnpkg-core/sources/MessageName.ts
  packages/acceptance-tests/pkg-tests-specs/sources/pnp.test.js
""",
        source="""repository: yarnpkg/berry
issue: https://github.com/yarnpkg/berry/issues/2452
pr: https://github.com/yarnpkg/berry/pull/2801
failing_ref (PR base / merge parent): 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
fixed_ref (squash merge commit): a2ea850802f3d05129edb179d902890744c03e65
head_sha: 0d6f061e93e6978606b83c96545a1dd1eee97521
merged_at: 2021-04-24T18:35:42Z
merged_by: arcanis
changed_files: packages/plugin-pnp/sources/PnpLinker.ts, packages/acceptance-tests/pkg-tests-specs/sources/pnp.test.js, CHANGELOG.md
pr_title: fix(plugin-pnp): delete stale build state when unplugged folder is missing
scout_note: not specimen-082/peerleft (bun.lock leftover packages vs optionalPeers mention after bun remove). not #1490 leftover dependenciesMeta.unplugged after yarn remove (open, no fixed_ref). not specimen-087 leftover pnpm path field. Distinct leftover: storedBuildState buildHash after .yarn/unplugged is removed vs never-built YN0007; PnP packageLocation still names the unplugged path. getBuildHash hashes path strings, not unplugged contents. yarn remove of the package already rebuilds storedBuildState from remaining buildablePackages.
""",
        answer_key="""KNOWN FIX (sealed): yarnpkg/berry PR 2801 squash merge a2ea850802f3d05129edb179d902890744c03e65.

PnpInstaller.unplugPackage recopied the zip when `.ready` was missing but left Project.storedBuildState alone. getBuildHash is sha512(globalHash + getBaseHash(locator) + unplugged path strings) and does not observe unplugged contents, so the leftover hash still matched and MUST_BUILD (YN0007) was skipped. Repair: when `.ready` is missing, `this.opts.project.storedBuildState.delete(locator.locatorHash)` before recopying, so the later comparison sees an omitted locator (same identity as never-built / first install). Added pnp.test.js case: first install YN0007, second no YN0007, rm .yarn/unplugged, third install YN0007.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (never-built YN0007 vs leftover already-built skip vs yarn-remove prune of locators that left the tree; storedBuildState hash vs PnP packageLocation vs missing unplugged files; path-string hash vs content)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two stores disagree after unplugged remove; buildHash ignores folder contents; yarn remove of the package is a different prune
ecosystem: yarn / node / PnP
mechanism_family: leftover-build-state, unplugged-folder-remove, pnp-packageLocation-path-hash

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "unplug_package_failing.ts": """// Reduced excerpt of PnpInstaller.unplugPackage on failing_ref
// packages/plugin-pnp/sources/PnpLinker.ts
// 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
// After rm -rf .yarn/unplugged, .ready is missing so the zip is recopied.
// storedBuildState is not cleared.

  private async unplugPackage(locator: Locator, fetchResult: FetchResult) {
    const unplugPath = pnpUtils.getUnpluggedPath(locator, {configuration: this.opts.project.configuration});
    this.unpluggedPaths.add(unplugPath);

    const readyFile = ppath.join(unplugPath, fetchResult.prefixPath, `.ready` as Filename);
    if (await xfs.existsPromise(readyFile))
      return new CwdFS(unplugPath);

    await xfs.mkdirPromise(unplugPath, {recursive: true});
    await xfs.copyPromise(unplugPath, PortablePath.dot, {baseFs: fetchResult.packageFs, overwrite: false});

    await xfs.writeFilePromise(readyFile, ``);

    return new CwdFS(unplugPath);
  }
""",
            "skip_rebuild_failing.ts": """// Reduced excerpt of the build-state skip on failing_ref
// packages/yarnpkg-core/sources/Project.ts
// 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
// MUST_BUILD = MessageName 7 = YN0007.

        const buildHash = getBuildHash(pkg, buildInfo.buildLocations);

        // No need to rebuild the package if its hash didn't change
        if (this.storedBuildState.get(pkg.locatorHash) === buildHash) {
          nextBState.set(pkg.locatorHash, buildHash);
          continue;
        }

        if (this.storedBuildState.has(pkg.locatorHash))
          report.reportInfo(MessageName.MUST_REBUILD, `${structUtils.prettyLocator(this.configuration, pkg)} must be rebuilt because its dependency tree changed`);
        else
          report.reportInfo(MessageName.MUST_BUILD, `${structUtils.prettyLocator(this.configuration, pkg)} must be built because it never has been before or the last one failed`);
""",
            "get_build_hash_failing.ts": """// Reduced excerpt of getBuildHash on failing_ref
// packages/yarnpkg-core/sources/Project.ts
// Hashes locator identity plus buildLocation path strings, not unplugged contents.
// Comment on the reconstruction: remove state from packages that got removed
// (locators that left buildablePackages). Case C keeps the locator in the tree.

    const getBuildHash = (locator: Locator, buildLocations: Array<PortablePath>) => {
      const builder = createHash(`sha512`);

      builder.update(globalHash);
      builder.update(getBaseHash(locator));

      for (const location of buildLocations)
        builder.update(location);

      return builder.digest(`hex`);
    };

    // We reconstruct the build state from an empty object because we want to
    // remove the state from packages that got removed
    const nextBState = new Map<LocatorHash, string>();
""",
            "leftover_identity_split.txt": """Registry / fixture:
  no-deps-scripted (in-tree PR 2801 test) — has install script
  @sentry/cli@1.62.0 (public #2452) — install script fetches sentry-cli binary

Case A (never built / first install):
  yarn install
  stdout contains YN0007 MUST_BUILD
  PnP packageLocation = .yarn/unplugged/<slug>/
  storedBuildState[locatorHash] = sha512(globalHash + baseHash + path strings)
  unplugged prefix contains .ready

Case B (second install, unplugged tree still on disk):
  yarn install
  no YN0007
  storedBuildState.get(locatorHash) === getBuildHash(...)

Case C (remove unplugged tree; package still a dependency):
  rm -rf .yarn/unplugged
  yarn install
  unplugPackage recopies zip (no .ready)
  getBuildHash unchanged (same path strings)
  leftover storedBuildState matches → no YN0007
  @sentry/cli: spawn …/sentry-cli ENOENT
  PnP packageLocation still names the unplugged directory

Case D (never installed):
  no PnP registry ident for the package
  no storedBuildState row
  no .yarn/unplugged/<slug>/ directory

Not this packet:
  bun.lock leftover packages vs optionalPeers mention after bun remove (specimen-082)
  leftover dependenciesMeta.unplugged after yarn remove (#1490, unfixed)
  finalizeInstallWithPnp deleting unused unplugged dirs for locators that left the tree
""",
        },
    )


def _complete_and_enqueue(spec_id: str) -> None:
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
                priority_reason="yarn leftover storedBuildState after unplugged remove; not bun 082 / not #1490",
                specimen=spec_id,
                lineage=TRIAL,
                phase="cambrian",
                extra={"trial": TRIAL},
            )
        return spec_id

    with_state(fn)


def main() -> None:
    spec_id = _claim_id()
    dest = SPECIMENS / spec_id
    try:
        path = emit(packet_for(spec_id))
        seed = write_seed(SPECIMENS / spec_id)
        update_index()
        _complete_and_enqueue(spec_id)
        print(path)
        print(seed)
        print(
            f"enqueued READY_R1_DREAM trial={TRIAL} specimen={spec_id} "
            "(dream.sh not launched; R1 already in flight)"
        )
    except Exception:
        if dest.is_dir() and not (dest / "manifest.yaml").exists():
            try:
                dest.rmdir()
            except OSError:
                pass
        raise


if __name__ == "__main__":
    main()
