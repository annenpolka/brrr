# OBSERVED

Public golang/go#65363 (closed 2026-04-29, gopherbot). CL 762602 (matloob) submitted as `8191cd88683192e9aa3f3a1c11e841f8f40a9a9d`. Failing world pinned on first parent `a2214422293d2c26ad389050f25460b3f2f00825`. Local `go work sync` was not performed on this lab host.

bcmills (issue comments): `go work sync` loads the module graph with workspace replaces, then reloads each work module individually with only that module's replaces. Workspace replace can hide requirements that would bump versions. Combined with `EditBuildList` error `continue`, the observed `go.mod` can stay at the workspace-selected identity.

On failing_ref, `runSync` after `EnterModule`:

```
changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
if err != nil {
    continue
}
if changed {
    ...
    modload.WriteGoMod(moduleLoader, ctx, modload.WriteOpts{})
}
```

`work_sync_replace.txt` is **not** on the failing revision. It is added by CL 762602.

Not this packet: specimen-084 (golang/mod sumdb tree-extension leftover). specimen-083 (derived go.sum zip vs mod). cargo git-lock SHA vs checkout (rust-lang/cargo#14230 open; PR 17275 closed unmerged).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
