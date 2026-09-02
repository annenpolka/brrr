# COMMANDS

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
