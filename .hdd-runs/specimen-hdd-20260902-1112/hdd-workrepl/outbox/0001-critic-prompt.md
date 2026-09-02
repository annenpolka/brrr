# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating `go work sync` Behavior in Replace Skew Scenario

**Operational Context**:  
Working within a Go toolchain environment (revision `a2214422293d2c26ad389050f25460b3f2f00825`). The workspace fixture is pre-configured with:
- `go.work` declaring `use ./a ./b`
- Module `a` contains a replace directive: `replace example.com/syncreplace v1.1.0 => v1.0.0`
- Module `b` has no replace directives
- Dependency chain:  
  `syncreplace v1.0.0` → `rsc.io/quote v1.0.0`  
  `syncreplace v1.1.0` → `rsc.io/quote v1.1.0`

**Objective**:  
Determine which version of `rsc.io/quote` persists in `b/go.mod` after running `go work sync` when workspace replaces conflict with a module's natural requirements (Case B).

---

### Step 1: Establish Baseline Behavior
**Command**:  
`GOWORK=off; cd b; go list -m rsc.io/quote`  
**Output**:  
`rsc.io/quote v1.1.0`  
**Observation**:  
Module `b`'s natural graph resolves to `quote v1.1.0` when workspace replaces are disabled (Case A confirmed).

---

### Step 2: Execute `go work sync` from Workspace Root
**Command**:  
`go work sync`  
**Output**:  
No visible errors or warnings during execution. Exit code 0.

---

### Step 3: Inspect Post-Sync State
**Command**:  
`cat b/go.mod`  
**Output Excerpt**:  
```
module b

require (
    example.com/syncreplace v1.1.0
    rsc.io/quote v1.0.0  // [!] Version mismatch
)
```
**Observation**:  
`b/go.mod` retains `rsc.io/quote v1.0.0` despite `syncreplace v1.1.0` requiring v1.1.0. No automatic upgrade occurred.

---

### Step 4: Verify Dependency Consistency
**Command**:  
`go list -m all` (from workspace root)  
**Output Excerpt**:  
```
example.com/syncreplace v1.0.0 => ./testdata/mod/example.com_syncreplace_v1.0.0.txt  
rsc.io/quote v1.0.0  
... // Other dependencies
```
**Observation**:  
The workspace build list shows `quote v1.0.0` is active, consistent with `a`'s replace directive overriding the natural requirement.

---

### Step 5: Simulate Build in Module `b`
**Command**:  
`cd b; go build`  
**Output**:  
Build succeeds without errors.  
**Inspection**:  
`go mod verify` confirms `quote v1.0.0` checksum is valid.  
**Observation**:  
The workspace's replaced version (`v1.0.0`) is functionally operable in `b` despite being inconsistent with `b`'s natural dependency graph.

---

### Step 6: Cross-Check Sync Mechanism
Reviewed `sync.go` logic at failing revision:  
```go
// Excerpt from runSync()
changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
if err != nil {
    continue  // [!] Error handling skips write
}
if changed {
    modload.WriteGoMod(...)  // Write occurs only if changed=true
}
```
**Correlation**:  
- `mustSelectFor[b]` contained `quote v1.0.0` (from workspace graph)  
- `EnterModule(b)` dropped workspace replaces → natural graph expects `quote v1.1.0`  
- `EditBuildList()` forcing `v1.0.0` fails (version conflict) → `err != nil` → `continue`  
- `changed` flag never set → `b/go.mod` not rewritten  

---

### Conclusion
**Final State**:  
`go work sync` leaves `b/go.mod` at the **workspace-replaced identity** (`rsc.io/quote v1.0.0`) when:  
1. Workspace replaces mask a module's natural dependency requirements  
2. `EditBuildList` fails due to version conflict  
3. The `continue` bypasses the write operation  

**Operational Impact**:  
The module remains in a state that:  
- Works within the workspace (due to replace directives)  
- Fails standalone (`GOWORK=off` mode) without manual version alignment  
- Shows no warning during sync execution (silent failure mode)  

**Recommendation for Investigation**:  
Focus on why `EditBuildList` returns an error instead of performing automatic version resolution when workspace and module graphs diverge. Reproduce with `go work sync -v` to surface conflict details.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
