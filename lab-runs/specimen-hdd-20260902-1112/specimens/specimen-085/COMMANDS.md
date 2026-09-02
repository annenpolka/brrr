# COMMANDS

```
# not executed on this lab host
# pnpm 10 object vs pnpm 11 string (PR 10911)

# case A object
# patchedDependencies.express@4.18.1.hash is 4eb8b160deadbeef
# patchedDependencies.express@4.18.1.path is patches/express@4.18.1.patch

# case B string
# patchedDependencies.express@4.18.1 is 4eb8b160deadbeef
# originalPatchFile?.hash is empty

# case C empty string
# case D omitted selector
```

Owned fixtures in `files/` are the two identities, not a pnpm run.
