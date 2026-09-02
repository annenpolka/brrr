# Reduced excerpt of ResourceInstanceObject.Encode on failing_ref
# internal/states/instance_object.go

func (o *ResourceInstanceObject) Encode(schema providers.Schema) (*ResourceInstanceObjectSrc, error) {
	// ... body marshal omitted ...

	var idJSON []byte
	// If the Identity is known and not null we can marshal it.
	if !o.Identity.IsNull() && o.Identity.IsWhollyKnown() && schema.Identity != nil {
		idJSON, err = ctyjson.Marshal(o.Identity, schema.Identity.ImpliedType())
		if err != nil {
			return nil, err
		}
	}

	return &ResourceInstanceObjectSrc{
		AttrsJSON:             src,
		IdentityJSON:          idJSON,
		IdentitySchemaVersion: uint64(schema.IdentityVersion),
		decodeIdentityCache:   o.Identity,
	}, nil
}
