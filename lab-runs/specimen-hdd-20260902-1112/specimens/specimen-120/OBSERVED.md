# OBSERVED

Public prefix-dev/pixi#3758 (closed 2025-05-20). PR 3782 squash `804d2360157ca9c3d9197a4519ea803d28220e59` (parent `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`). Local pixi was not performed on this lab host.

Issue body: `pixi run multiple` never reports cache hit; `pixi run single` and `pixi run create-all` (two distinct task names) do.

On failing_ref, cache filename is run-environment + task-name. Rendered inputs/outputs and ArgValues are not that filename. `TaskHash::computation_hash` still hashes file contents inside the file; the *name* of the file is the leftover identity.

`NameHash` / `task_args_hash` are **not** on the failing revision. They are added by PR 3782.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH; template name `build-*` vs MATCH instantiation). Pixi leftover is one named task with two argument instantiations sharing `env-name.json`.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
