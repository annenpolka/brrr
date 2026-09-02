# Reduced excerpt of configschema.Object type helpers on failing_ref
# internal/configs/configschema/implied_type.go

func (o *Object) ImpliedType() cty.Type {
	return o.specType().WithoutOptionalAttributesDeep()
}

func (o *Object) specType() cty.Type {
	if o == nil {
		return cty.EmptyObject
	}
	attrTys := make(map[string]cty.Type, len(o.Attributes))
	for name, attrS := range o.Attributes {
		if attrS.NestedType != nil {
			attrTys[name] = attrS.NestedType.specType()
		} else {
			attrTys[name] = attrS.Type
		}
	}
	// ...
	return cty.Object(attrTys)
}
