# TASK

`go work sync` can leave a workspace module's `go.mod` at the identity selected under **workspace replaces**, even when that module itself has no replace and its own graph would pick a higher requirement.

On failing_ref `a2214422293d2c26ad389050f25460b3f2f00825`, `runSync` (`src/cmd/go/internal/workcmd/sync.go`) first loads the workspace graph (`LoadModGraph` / `LoadPackages` with workspace replaces). It records `mustSelectFor[m]` as the module versions seen for packages in each work module. Then `EnterModule` switches to **single-module** mode at that module's root (that module's `go.mod` replaces only). `EditBuildList(..., nil, mustSelectFor[m])` tries to force the workspace-selected versions. On error it does `continue`.

In-tree after the repair (not on failing_ref): `src/cmd/go/testdata/script/work_sync_replace.txt`.

```
go.work: use ./a ./b
a/go.mod: replace example.com/syncreplace v1.1.0 => example.com/syncreplace v1.0.0
          require example.com/syncreplace v1.1.0 and rsc.io/quote v1.0.0
b/go.mod: no replace
          require example.com/syncreplace v1.1.0 and rsc.io/quote v1.0.0
syncreplace v1.0.0 requires rsc.io/quote v1.0.0
syncreplace v1.1.0 requires rsc.io/quote v1.1.0
```

Workspace load applies a's replace, so syncreplace is v1.0.0 and quote stays v1.0.0. Module b has no replace: its own graph wants syncreplace v1.1.0 / quote v1.1.0.

Case A — `GOWORK=off` in module b (`go list -m rsc.io/quote`):
  identity is b's own graph (quote v1.1.0 through syncreplace v1.1.0)
  no leftover workspace replace

Case B — `go work sync` from the workspace root:
  first pass uses workspace replaces (a's replace hides syncreplace v1.1.0's quote bump)
  `mustSelectFor[b]` therefore contains the workspace-selected quote v1.0.0
  `EnterModule(b)` drops a's replace
  `EditBuildList` forcing those versions can conflict
  failing_ref: `if err != nil { continue }` so b/go.mod is not rewritten
  leftover: b/go.mod still names quote v1.0.0 (workspace-replace identity)

Case C — `go work sync` when every work module has the same replace as the workspace:
  no replace skew
  not this leftover

Case D — `go work edit -replace` override in go.work that both modules share:
  workspace and module graphs agree on the override
  not the silent-continue leftover

The developer wants to know which identity `go work sync` actually left in `b/go.mod` for case B: leftover workspace-replace versions (quote v1.0.0, unsynced), b's own replace-free versions (quote v1.1.0), or omitted (no write because of continue vs fatal).
