# TASK

`ResourceInstanceObjectSrc.Decode` of a state object that still carries identity JSON, against a provider schema whose `Identity` is nil, does not yield a usable identity.

State instance (`aws_instance.web`):

```
Status: ready
AttrsJSON: {"id":"foo","foo":"bar"}
IdentitySchemaVersion: 0
IdentityJSON: {"id": "foo"}
```

Provider schema case A (current provider reports no resource identity):

```
Body: attributes id (computed string), foo (optional/computed string)
Identity: nil
IdentityVersion: 0
```

`Decode(schema)` on hashicorp/terraform `aed61af66c5b16f40d45a573be9ebdea7cce2b36` takes the `IdentityJSON != nil` branch and calls `schema.Identity.ImpliedType()` then `ctyjson.Unmarshal`.

Same state against case B (identity schema present, `id` required string, NestingSingle) decodes identity as `{id: "foo"}`.

Case C: case A's nil identity schema, but `IdentityJSON` also nil. `Decode` skips the identity branch (zero `cty.Value`). `Encode` on the same schema already requires `schema.Identity != nil` before writing `IdentityJSON`.

In-tree `TestContext2Plan_resource_identity_refresh` / `"identity type mismatch"` on that revision: `IdentityJSON` `{"arn":"foo"}` versus an identity schema that only has `id` yields

```
failed to decode identity: unsupported attribute "arn". This is most likely a bug in the Provider, providers must not change the identity schema without updating the identity schema version
```

The developer wants to know which identity `Decode` actually produced for leftover `IdentityJSON` when the current provider schema had no identity schema: present object, typed null, omitted/zero value, or the same unsupported-attribute error class as a schema mismatch.
