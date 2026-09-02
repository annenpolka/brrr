# COMMANDS

```
# in-tree, not executed on this lab host

# case A — parent 60d3a328bc047c211f75936d54003323ee7ee245
# pnpm install with patchedDependencies: { 'is-positive@1.0.0': <patchPath> }
# lockfile.patchedDependencies['is-positive@1.0.0'] is
#   { path: <relative posix path>, hash: <patchFileHash> }

# case B — 223b9b2e993fcd8766fb0681fc03a349462f1916 write
# same install; lockfile.patchedDependencies['is-positive@1.0.0'] is <patchFileHash>
# pkg-manager/core/test/install/patch.ts expects the bare string

# case C — 223b9b2 read of a case A lockfile
# convertToLockfileObject spreads rest.patchedDependencies with no rewrite
# groupPatchedDependencies: const hash = patchedDependencies[key]
# getOutdatedLockfileSetting: ramda.equals leftover object vs current hash strings

# case D — selector omitted, patch file still on disk
```

Not executed on this lab host.
