# OBSERVED

Public jdx/mise#10114 merged 2026-05-28. Squash merge `f38bab024878162972660d16935ac5cc8340a582` (parent `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`). Discussion #9978. Local mise execution was not performed on this lab host.

On failing_ref, `Upgrade` cleanup after rebuild_for_toolset:

```
let versions_needed_by_tracked =
    get_versions_needed_by_tracked_configs(config, false, false).await?;
```

Comment on failing_ref: upgrade passes false because it checks what tracked configs resolve to after an upgrade, before their lockfiles have been updated. That false is applied to **all** tracked configs, including siblings whose lockfiles were not the upgrade target.

`get_versions_needed_by_tracked_configs` only reads `Lockfile::read` when `use_locked_version` is true. Foo's `[[tools.dummy]] version = "1.0.0"` is therefore not in the keep-set. Cleanup uninstalls `dummy@1.0.0` if bar's upgrade succeeded.

The e2e sibling-lock block is **absent** on `2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c`. It is added by PR 10114.

Not this packet: specimen-006/022/023/102 (uv git vs directory source kinds). specimen-078 (go testcache omits buildid). specimen-089 (yarn PnP leftover locator).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
