# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

```
# not executed on this lab host
# failing_ref a2214422293d2c26ad389050f25460b3f2f00825
# src/cmd/go/internal/workcmd/sync.go runSync
# src/cmd/go/testdata/script/work_sync_replace.txt (on CL 762602, not failing_ref)

# public shape:
# go.work use ./a ./b
# a replace syncreplace v1.1.0 => v1.0.0
# b no replace
# go work sync
# failing: EditBuildList error continue; b/go.mod leftover workspace quote v1.0.0
```

Source-backed only. Do not execute untrusted checkouts on the host.

golang/go
  src/cmd/go/internal/workcmd/sync.go
  src/cmd/go/testdata/script/work_sync_replace.txt
  src/cmd/go/testdata/mod/example.com_syncreplace_v1.0.0.txt
  src/cmd/go/testdata/mod/example.com_syncreplace_v1.1.0.txt

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  go.work use ./a ./b
  a replace syncreplace v1.1.0 => v1.0.0
  b no replace
  syncreplace v1.0.0 requires rsc.io/quote v1.0.0
  syncreplace v1.1.0 requires rsc.io/quote v1.1.0

Case A (GOWORK=off in b):
  quote identity = v1.1.0
  no leftover workspace replace

Case B (go work sync, failing_ref):
  workspace graph applies a's replace
  mustSelectFor[b] has quote v1.0.0
  EnterModule(b) has no replace
  EditBuildList can err; continue
  leftover: b/go.mod still quote v1.0.0

Case C (every module has the same replace):
  no replace skew
  not leftover

Case D (go.work replace override shared):
  graphs agree
  not silent-continue leftover

Not this packet:
  golang/mod sumdb tree-extension leftover (specimen-084)
  derived go.sum zip vs mod (specimen-083)
  cargo lock SHA vs checkout (cargo#14230 unfixed)

### sync_editbuildlist_failing.go

// Reduced excerpt of runSync on failing_ref
// src/cmd/go/internal/workcmd/sync.go
// a2214422293d2c26ad389050f25460b3f2f00825
// Workspace versions are mustSelect. EnterModule drops other modules' replaces.
// EditBuildList error continue leaves leftover go.mod.

		changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
		if err != nil {
			continue
		}
		if changed {
			modload.LoadPackages(moduleLoader, ctx, modload.PackageOpts{
				Tags:                     imports.AnyTags(),
				Tidy:                     true,
				VendorModulesInGOROOTSrc: true,
				ResolveMissingImports:    false,
				LoadTests:                true,
				AllowErrors:              true,
				SilenceMissingStdImports: true,
				SilencePackageErrors:     true,
			}, "all")
			modload.WriteGoMod(moduleLoader, ctx, modload.WriteOpts{})
		}

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
