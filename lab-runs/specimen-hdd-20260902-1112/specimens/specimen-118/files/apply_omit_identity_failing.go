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
