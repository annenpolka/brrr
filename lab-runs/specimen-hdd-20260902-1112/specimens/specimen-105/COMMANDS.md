```
# not executed on this lab host
# failing_ref df96f06c70aaba8aa9152afc7726a78101694cdb
# src/graphs.rs populate_packages / remove_root_pkg_by_id
# tests/specs/config_changes/remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt (on the PR, not failing_ref)

# public shape:
# workspace drops jsr:@pkg/a while jsr:@pkg/b remains
# both named npm:dep@1
# failing: jsr["@pkg/b"].dependencies still "npm:dep@1" after specifiers lost it
```

Source-backed only. Do not execute untrusted checkouts on the host.
