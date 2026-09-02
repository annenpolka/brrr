```
# not executed on this lab host
# failing_ref 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c
# src/cli/upgrade.rs get_versions_needed_by_tracked_configs(config, false, false)
# src/toolset/mod.rs Lockfile::read gated on use_locked_version
# e2e/cli/test_upgrade sibling tracked lock block (on the PR, not failing_ref)

# public shape:
# foo and bar both dummy=latest locked 1.0.0
# cd bar && mise upgrade dummy@2.0.0
# failing: foo lock still 1.0.0, install of 1.0.0 gone
```

Source-backed only. Do not execute untrusted checkouts on the host.
