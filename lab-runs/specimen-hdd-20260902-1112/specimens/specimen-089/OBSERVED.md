# OBSERVED

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
