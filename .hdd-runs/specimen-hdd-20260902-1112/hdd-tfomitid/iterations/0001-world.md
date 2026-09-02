# Current situation

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
