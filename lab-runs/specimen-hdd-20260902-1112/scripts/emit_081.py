#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet specimen-081 (terraform identity JSON vs absent identity schema).

Scout assigned specimen-080; that slot was already occupied by a DERIVED_VERIFIED
local-fixture. This packet is the terraform provider-schema-identity find.
"""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

SPEC_ID = "specimen-081"


packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-081
kind: REAL_SOURCE_BACKED
repository: hashicorp/terraform
failing_ref: aed61af66c5b16f40d45a573be9ebdea7cce2b36
fixed_ref: 62540da0153899b20f7808026e9c8afa2b5a6112
source_issue: none
source_pr: https://github.com/hashicorp/terraform/pull/37709
mechanism_tags:
  - provider-schema-identity
  - leftover-identity-json
  - encode-decode-identity-guard
ecosystem: terraform
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

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
""",
    observed="""# OBSERVED

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
""",
    commands="""# COMMANDS

```
# in-tree on failing_ref aed61af66c5b16f40d45a573be9ebdea7cce2b36
# (not executed on this lab host)

go test ./internal/terraform -run 'TestContext2Plan_resource_identity_refresh$' -count=1
# "identity type mismatch": failed to decode identity: unsupported attribute "arn"...
# "no previous identity": identity {id: "foo"} after refresh-only plan

# Decode leftover identity JSON against a schema with Identity == nil
# State:
#   AttrsJSON: {"id":"foo","foo":"bar"}
#   IdentityJSON: {"id": "foo"}
#   IdentitySchemaVersion: 0
# Schema:
#   Body: aws_instance id/foo
#   Identity: nil
# Decode takes the IdentityJSON != nil branch and calls schema.Identity.ImpliedType()
```

Not executed on this lab host.
""",
    tree="""hashicorp/terraform
  internal/states/instance_object_src.go
  internal/states/instance_object.go
  internal/providers/provider.go
  internal/configs/configschema/implied_type.go
  internal/terraform/context_plan_identity_test.go
""",
    source="""repository: hashicorp/terraform
pr: https://github.com/hashicorp/terraform/pull/37709
issue: none (PR-only)
failing_ref (squash-merge parent): aed61af66c5b16f40d45a573be9ebdea7cce2b36
fixed_ref (squash merge commit): 62540da0153899b20f7808026e9c8afa2b5a6112
head_sha: a175b1750b3c3118721c4f2ad11f87c3723c3f08
merged_at: 2025-10-06T08:15:54Z
merged_by: dbanck
changed_files: internal/states/instance_object_src.go, internal/states/instance_object_test.go, internal/terraform/context_plan_identity_test.go
pr_title: search: Drop identity from state if no identity schema is present
scout_note: assigned specimen-080; that id already held DERIVED_VERIFIED local-fixture (pip extra marker). Emitted as specimen-081.
""",
    answer_key="""KNOWN FIX (sealed): hashicorp/terraform PR 37709 squash merge 62540da0153899b20f7808026e9c8afa2b5a6112.

Decode unmarshaled IdentityJSON whenever it was non-nil, using schema.Identity.ImpliedType(). Encode already required schema.Identity != nil. A provider without a resource identity schema (downgrade) therefore fed leftover identity JSON through ImpliedType on a nil *configschema.Object (EmptyObject) and surfaced the unsupported-attribute provider-bug error instead of treating identity as absent. Repair: also require schema.Identity != nil before decoding, so leftover identity is skipped; a later Encode writes no IdentityJSON, and the added refresh-only downgrade test expects a null identity.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (IdentityJSON present + schema.Identity nil vs IdentityJSON present + identity schema with id; Encode already omits IdentityJSON when Identity is nil; type-mismatch Decode error vs successful refresh identity)
reproducibility: source-backed PR + pinned squash parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — leftover identity JSON is decoded through the current provider identity schema, which may be absent
ecosystem: terraform / go
mechanism_family: provider-schema-identity, leftover-identity-json, encode-decode-identity-guard

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "decode_identity_failing.go": """# Reduced excerpt of ResourceInstanceObjectSrc.Decode on failing_ref
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
""",
        "encode_identity.go": """# Reduced excerpt of ResourceInstanceObject.Encode on failing_ref
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
""",
        "implied_type_nil_object.go": """# Reduced excerpt of configschema.Object type helpers on failing_ref
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
""",
        "identity_schema_split.txt": """State instance (all cases unless noted):
  aws_instance.web
  AttrsJSON: {"id":"foo","foo":"bar"}
  IdentitySchemaVersion: 0
  IdentityJSON: {"id": "foo"}
  Status: ready

providers.Schema case A (no resource identity on current provider):
  Body: aws_instance { id computed string, foo optional/computed string }
  Identity: nil
  IdentityVersion: 0

providers.Schema case B (identity schema present):
  Body: same as A
  Identity: Object { id required string, NestingSingle }
  IdentityVersion: 0

providers.Schema case C:
  same as A, but IdentityJSON is nil / empty

In-tree refresh subtests on failing_ref (all use case-B-like IdentityTypes):
  "no previous identity": IdentityJSON empty + identity schema with id
    -> after refresh-only plan, identity {id: "foo"}
  "identity type mismatch": IdentityJSON {"arn":"foo"} + identity schema with only id
    -> failed to decode identity: unsupported attribute "arn"...

Decode on failing_ref, leftover IdentityJSON vs case A:
  takes IdentityJSON != nil branch
  calls schema.Identity.ImpliedType()
  Object.specType on nil receiver returns cty.EmptyObject
""",
    },
)


if __name__ == "__main__":
    dest = SPECIMENS / SPEC_ID
    if dest.exists():
        raise SystemExit(f"{dest} already exists; refusing to overwrite")
    path = emit(packet)
    seed = write_seed(SPECIMENS / SPEC_ID)
    print(path)
    print(seed)
    update_index()
