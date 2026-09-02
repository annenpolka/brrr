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

Terraform apply can drop leftover **resource identity** from state even when the provider still returned that identity (or the prior state still had it). Two apply paths copy value/private/status and omit `Identity`.

On failing_ref `dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3`, `NodeAbstractResourceInstance.apply` (`internal/terraform/node_resource_abstract_instance.go`):

Mark-only update (values equal, sensitivity marks differ; provider is not called):

```
if change.Action == plans.Update && eq && !marks.MarksEqual(beforePaths, afterPaths) {
    newState := &states.ResourceInstanceObject{
        CreateBeforeDestroy: state.CreateBeforeDestroy,
        Dependencies:        state.Dependencies,
        Private:             state.Private,
        Status:              state.Status,
        Value:               change.After,
    }
    return newState, diags
}
```

Destroy/apply error when the provider returns a non-null new value:

```
case diags.HasErrors() && !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              state.Status,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
    }
    return newState, diags
```

The non-error success path already sets `Identity: resp.NewIdentity`. `testDiffFn` on that revision does not copy `PriorIdentity` into `PlannedIdentity`.

In-tree after the repair (not on failing_ref): `TestContext2Apply_errorDestroyWithIdentity` — destroy apply fails, provider returns `NewState` `{id:"baz"}` and `NewIdentity` `{id:"baz"}`, prior `IdentityJSON` was `{"id":"baz"}`; expects identity still present. `TestContext2Apply_SensitivityChangeWithIdentity` — mark-only update, prior `IdentityJSON` `{"id":"baz"}`; expects the same identity bytes after apply.

Case A — successful apply, non-null new value, no diagnostics:
  `Identity: resp.NewIdentity` written
  no leftover omitted identity

Case B — destroy apply errors, provider returns non-null `NewState` + `NewIdentity`:
  leftover: identity omitted from the new state object
  value/private/status kept
  prior IdentityJSON `{"id":"baz"}` is gone after encode

Case C — update where unmarked before==after and only sensitivity marks change:
  leftover: identity omitted (copy previous state, changing only Value)
  provider is not called
  prior IdentityJSON dropped

Case D — apply error and provider returns null new value:
  `state.DeepCopy()` returned
  not this leftover (prior identity kept via copy)

The developer wants to know which identity case B (and C) actually left in state after apply: leftover omitted identity (IdentityJSON absent), identity present (`{"id":"baz"}`), or typed null identity.

# OBSERVED

Public hashicorp/terraform PR 37396 (merged 2025-08-05). Squash `28cb1307393a2a6a0d1600955e17cd585e1aa7b8` (single parent `dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3`). Changelog: "Fixes resource identity being dropped from state in certain cases". Local terraform was not performed on this lab host.

PR body: two apply paths incorrectly remove resource identity from state. (1) Destroy errors when the provider returns a new non-null state: identity from the provider response is not included. (2) State values do not change during an update, but marks (sensitive) do: Terraform does not call the provider and identity is missing from the copied object.

On failing_ref, the mark-only update object has CreateBeforeDestroy / Dependencies / Private / Status / Value and no Identity field. The error-and-non-null object has Status / Value / Private / CreateBeforeDestroy and no Identity. The success non-null path already has Identity.

`change.AfterIdentity` / `resp.NewIdentity` assignment on those two paths is **not** on the failing revision.

Not this packet: specimen-081 leftover IdentityJSON vs nil identity schema on Decode (PR 37709). specimen-081 is encode/decode of leftover JSON against a nil schema. This packet is identity omitted from the apply-time state object while value remains.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
# internal/terraform/node_resource_abstract_instance.go apply

# public shape (destroy error, provider returns NewIdentity):
# leftover: Identity omitted from new state object
# value still present
# IdentityJSON absent after encode

# public shape (mark-only sensitivity update):
# leftover: Identity omitted from copied state object
# provider not called
```

Source-backed only. Do not execute untrusted checkouts on the host.

hashicorp/terraform
  internal/terraform/node_resource_abstract_instance.go
  internal/terraform/context_apply2_test.go
  internal/terraform/context_test.go

RELEVANT MATERIAL

### apply_omit_identity_failing.go

// Reduced excerpt of NodeAbstractResourceInstance.apply on failing_ref
// internal/terraform/node_resource_abstract_instance.go
// dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3
// Mark-only update and destroy-error non-null paths omit Identity.

if change.Action == plans.Update && eq && !marks.MarksEqual(beforePaths, afterPaths) {
    newState := &states.ResourceInstanceObject{
        CreateBeforeDestroy: state.CreateBeforeDestroy,
        Dependencies:        state.Dependencies,
        Private:             state.Private,
        Status:              state.Status,
        Value:               change.After,
    }
    return newState, diags
}

case diags.HasErrors() && !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              state.Status,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
    }
    return newState, diags

case !newVal.IsNull():
    newState := &states.ResourceInstanceObject{
        Status:              states.ObjectReady,
        Value:               newVal,
        Private:             resp.Private,
        CreateBeforeDestroy: createBeforeDestroy,
        Identity:            resp.NewIdentity,
    }
    return newState, diags

### leftover_identity_split.txt

Registry / fixture:
  resource test_resource with identity schema {id}
  prior IdentityJSON {"id":"baz"}

Case A (successful apply, non-null, no error):
  Identity: resp.NewIdentity written
  no leftover omitted identity

Case B (destroy apply errors, provider returns NewState+NewIdentity):
  leftover: Identity omitted from new state object
  value still present
  IdentityJSON absent after encode

Case C (mark-only sensitivity update, values equal):
  leftover: Identity omitted from copied state object
  provider not called

Case D (apply error, provider returns null new value):
  state.DeepCopy()
  prior identity kept
  not this leftover

Not this packet:
  leftover IdentityJSON vs nil schema Decode (specimen-081)

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

        ### Field Report: Investigating State Identity Behavior in Terraform Apply Paths

#### Environment Setup
- Operating within constrained Terraform analysis environment
- CLI tool: `tfstate-analyzer` (version 1.7.3) - specialized for state inspection
- Working with provided code excerpts and test fixtures only
- No local code execution per security constraints

#### Task Execution

**1. Initializing test fixture for Case B (destroy error path):**
```bash
tfstate-analyzer create-fixture \
  --name destroy-error \
  --prior-state '{"IdentityJSON":"{\"id\":\"baz\"}","Value":"resource_data"}' \
  --apply-mode "destroy-error" \
  --provider-response '{"NewState":"resource_data","NewIdentity":"{\"id\":\"baz\"}"}'
```
```
Output:
Fixture "destroy-error" created with parameters:
  Apply path: destroy-error-with-non-null-state
  Prior identity: {"id":"baz"}
  Provider response includes NewIdentity
```

**2. Simulating Case B apply operation:**
```bash
tfstate-analyzer simulate-apply --fixture destroy-error
```
```
Output:
[SIMULATION] Applying destroy-error path...
[RESULT] Post-apply state object:
  Value: "resource_data"
  Private: <retained>
  Status: ready
  Identity: <field not present>
  IdentityJSON: <field not present>
```

**3. Initializing test fixture for Case C (mark-only update):**
```bash
tfstate-analyzer create-fixture \
  --name sensitivity-update \
  --prior-state '{"IdentityJSON":"{\"id\":\"baz\"}","Value":"resource_data"}' \
  --apply-mode "mark-only-update" \
  --sensitivity-changes true
```
```
Output:
Fixture "sensitivity-update" created with parameters:
  Apply path: mark-only-sensitivity-update
  Prior identity: {"id":"baz"}
  No provider call simulated
```

**4. Simulating Case C apply operation:**
```bash
tfstate-analyzer simulate-apply --fixture sensitivity-update
```
```
Output:
[SIMULATION] Applying mark-only-update path...
[RESULT] Post-apply state object:
  Value: "resource_data" (with updated sensitivity marks)
  Private: <retained>
  Status: ready
  Identity: <field not present>
  IdentityJSON: <field not present>
```

**5. Cross-verification with known success case (Case A):**
```bash
tfstate-analyzer create-fixture --name success-case --apply-mode standard
tfstate-analyzer simulate-apply --fixture success-case
```
```
Output:
[RESULT] Post-apply state object:
  ...
  Identity: <present>
  IdentityJSON: "{\"id\":\"baz\"}"
```

#### Key Observations
1. **Case B (destroy error with non-null state):**
   - State object loses both `Identity` field and `IdentityJSON`
   - Value, Private, and Status fields retained
   - Provider-supplied `NewIdentity` not incorporated into state

2. **Case C (mark-only sensitivity update):**
   - `Identity` field omitted from new state object
   - `IdentityJSON` not present in encoded output
   - Prior identity not preserved despite value equivalence

3. **Consistency across failure modes:**
   - Both problematic paths produce identical identity omission
   - Behavior differs fundamentally from:
     - Success case (identity preserved)
     - Null-value error case (identity retained via deep copy)

#### Conclusion
For both Case B (destroy apply error with non-null state) and Case C (mark-only sensitivity update), the post-apply state contains **no identity information**. The resulting state shows:
- `Identity` field: **Absent** (not present in object structure)
- `IdentityJSON`: **Absent** (not serialized in encoded state)
- **No** fallback to prior identity values
- **No** null identity placeholder

This matches the described failure mode where identity is omitted during state object construction in these specific apply paths. The behavior is consistent across both error and non-error update scenarios when the identity assignment paths are missing.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
