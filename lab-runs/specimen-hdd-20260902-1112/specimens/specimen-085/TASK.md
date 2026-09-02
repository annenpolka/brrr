# TASK

A pnpm lockfile's `patchedDependencies` entry for a selector can be either an object `{ path, hash }` or a bare hash string.

Case A — lockfile v9 / pre-simplify (object):

```
patchedDependencies:
  express@4.18.1:
    path: patches/express@4.18.1.patch
    hash: 4eb8b160deadbeef
```

A reader that takes `entry.hash` gets `4eb8b160deadbeef`. A reader that treats the entry as a string gets nothing useful.

Case B — pnpm 11+ simplified lockfile (selector → hash string):

```
patchedDependencies:
  express@4.18.1: 4eb8b160deadbeef
```

A reader that still does `entry.hash` / `originalPatchFile?.hash` on a string gets **empty**. Frozen install then fails with `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH` because the current patchedDependencies configuration does not match the value found in the lockfile.

Case C — selector present with empty string hash:

```
patchedDependencies:
  express@4.18.1: ""
```

Case D — selector missing from `patchedDependencies` while a `patches/` file still exists.

The developer wants to know which identity the lockfile actually contained for `express@4.18.1`: path+hash object, hash-only string, empty hash, or omitted.
