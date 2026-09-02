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
