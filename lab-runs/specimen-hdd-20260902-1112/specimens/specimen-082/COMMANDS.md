# COMMANDS

```
# in-tree on failing_ref c08f665367451debfc9a71799f1f29eba776e4a3
# (not executed on this lab host)
# registry fixtures: optional-peer-deps@1.0.0, no-deps@1.0.0 (Verdaccio test registry)

# case A
bun add -D optional-peer-deps@1.0.0
# bun.lock has no packages entry prefix "no-deps": ["no-deps@"

# case B
bun add no-deps@1.0.0
# bun.lock now contains "no-deps": ["no-deps@
bun remove no-deps
# package.json no longer lists no-deps
# Package::clone still walks the optional-peer resolution slot hoist filled in step 2
# and may push PendingResolution onto clone_queue

# case C (control)
# package.json already has optional-peer-deps@1.0.0 and one-dep@1.0.0 (hard dep no-deps@1.0.1)
bun add no-deps@1.0.1
bun remove no-deps
# bun.lock still contains a packages entry for no-deps
```

Not executed on this lab host.
