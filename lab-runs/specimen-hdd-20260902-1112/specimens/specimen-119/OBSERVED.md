# OBSERVED

Public prefix-dev/pixi#3758 (closed) / PR 3782. Failing world: prefix-dev/pixi
`1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05` (first parent of squash
`804d2360157ca9c3d9197a4519ea803d28220e59`). Local pixi was not performed
on this lab host.

Issue: task cache filename is run-environment + task-name. Parametrized
depends-on with different args share leftover cache identity.

On failing_ref, `cache_name` is:

```
format!("{}-{}.json", self.run_environment.name(), self.name().unwrap_or("default"))
```

`can_skip` / `save_cache` join that name onto `task_cache_folder()`.
`task_args_hash` is **not** on the failing revision. It is added by PR 3782
(NameHash of rendered inputs/outputs; filename becomes
`env-name-<args-hash>.json`).

Public report (nichmor): `create` with A.txt writes a cache file; `create`
with B.txt sees a mismatched recorded hash and overwrites the same file;
the next A invocation misses.

Not this packet: specimen-115 (go-task leftover wildcard checksum omitting
MATCH; `.task/checksum/<template>`). specimen-076/088/104 (gradle compiler
fingerprints).

This packet does not include a local clone. Do not execute untrusted
checkouts on the host.
