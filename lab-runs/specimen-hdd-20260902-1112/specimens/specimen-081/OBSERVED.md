# OBSERVED

Public hashicorp/terraform PR 37709. Failing world in `internal/states/instance_object_src.go` around squash-merge parent `aed61af66c5b16f40d45a573be9ebdea7cce2b36`.

`providers.Schema` holds both the resource body and an optional identity object:

```
type Schema struct {
    Version int64
    Body    *configschema.Block

    IdentityVersion int64
    Identity        *configschema.Object
}
```

`GetProviderSchema` is documented as merging identity schemas into that `Identity` field. A provider version without resource identity leaves `Identity` nil.

`Decode` on that revision:

```
var identity cty.Value
if os.decodeIdentityCache != cty.NilVal {
    identity = os.decodeIdentityCache
} else if os.IdentityJSON != nil {
    identity, err = ctyjson.Unmarshal(os.IdentityJSON, schema.Identity.ImpliedType())
    if err != nil {
        return nil, fmt.Errorf("failed to decode identity: %s. This is most likely a bug in the Provider, providers must not change the identity schema without updating the identity schema version", err.Error())
    }
}
```

Comment on `Decode`: "If the object has an identity, the schema must also contain a resource identity schema for the identity to be decoded."

`configschema.Object.ImpliedType` calls `specType()`. `specType` on a nil receiver returns `cty.EmptyObject`:

```
func (o *Object) specType() cty.Type {
    if o == nil {
        return cty.EmptyObject
    }
    ...
}
```

`Encode` on the same revision already skips marshaling identity unless the schema pointer is present:

```
if !o.Identity.IsNull() && o.Identity.IsWhollyKnown() && schema.Identity != nil {
    idJSON, err = ctyjson.Marshal(o.Identity, schema.Identity.ImpliedType())
```

In-tree refresh tests (`internal/terraform/context_plan_identity_test.go`, `TestContext2Plan_resource_identity_refresh`) on that revision always attach `IdentityTypes` for `aws_instance`. Documented subtests:

- `"no previous identity"`: `IdentityJSON` empty, identity schema has `id` → after refresh-only plan, identity is `{id: "foo"}` (from `ReadResource`)
- `"identity type mismatch"`: `IdentityJSON` `{"arn":"foo"}`, identity schema has only `id` → Decode error `failed to decode identity: unsupported attribute "arn"...`

There is no in-tree subtest on that revision whose provider schema sets `Identity` to nil while `IdentityJSON` is still `{"id": "foo"}`.

This packet does not include a local clone; treat the snippets and schema split as the world. Do not execute untrusted checkouts on the host.
