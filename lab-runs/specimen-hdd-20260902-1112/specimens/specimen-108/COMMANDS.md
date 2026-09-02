```
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
