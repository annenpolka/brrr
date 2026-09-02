# Reduced excerpt of ResourceInstanceObjectSrc.Decode on failing_ref
# internal/states/instance_object_src.go
# schema is providers.Schema for the current provider version.

func (os *ResourceInstanceObjectSrc) Decode(schema providers.Schema) (*ResourceInstanceObject, error) {
	var val cty.Value
	var err error
	attrsTy := schema.Body.ImpliedType()
	// ... AttrsJSON / AttrsFlat decode omitted ...

	var identity cty.Value
	if os.decodeIdentityCache != cty.NilVal {
		identity = os.decodeIdentityCache
	} else if os.IdentityJSON != nil {
		identity, err = ctyjson.Unmarshal(os.IdentityJSON, schema.Identity.ImpliedType())
		if err != nil {
			return nil, fmt.Errorf("failed to decode identity: %s. This is most likely a bug in the Provider, providers must not change the identity schema without updating the identity schema version", err.Error())
		}
	}

	return &ResourceInstanceObject{
		Value:    val,
		Identity: identity,
		Status:   os.Status,
	}, nil
}
