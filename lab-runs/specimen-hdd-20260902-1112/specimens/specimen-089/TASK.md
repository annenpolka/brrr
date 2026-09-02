# TASK

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
