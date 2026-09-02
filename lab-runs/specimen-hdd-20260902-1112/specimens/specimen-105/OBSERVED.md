# OBSERVED

Public denoland/deno_lockfile#62 merged 2025-10-16. Squash merge `3ef94bed3135eeae91515f8451a67de62094fe34` (parent `df96f06c70aaba8aa9152afc7726a78101694cdb`). Consumer bump denoland/deno#30998 merge `e43662812db4f1c9c51aec875781d80593727313` (deno_lockfile 0.32.1 → 0.32.2). Local Deno execution was not performed on this lab host.

On failing_ref, `populate_packages` writes specifiers from `root_packages` first, then copies each JSR package's `dependencies` with no filter:

```
dependencies: package
  .dependencies
  .into_iter()
  .map(|req| req.into_jsr_dep())
  .collect(),
```

`remove_root_pkg_by_id` for JSR ids pushes walked dependency ids onto `root_ids_to_remove` (including npm ids looked up through `root_packages`) and then `root_packages.retain` drops them. JSR package structs that were not themselves removed keep the old BTreeSet.

The spec file `remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt` is **absent** on `df96f06c70aaba8aa9152afc7726a78101694cdb`. It is added by PR 62.

Not this packet: specimen-004 (npm leftover metadata download). specimen-082 (bun optional-peer leftover). specimen-095 (npm nested overrides leftover). specimen-101 (cargo SCP-like gitmodules vs ssh:// fetch).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
