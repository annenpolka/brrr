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

# COMMANDS

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

hashicorp/terraform
  internal/states/instance_object_src.go
  internal/states/instance_object.go
  internal/providers/provider.go
  internal/configs/configschema/implied_type.go
  internal/terraform/context_plan_identity_test.go

RELEVANT MATERIAL

### decode_identity_failing.go

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

### encode_identity.go

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

### identity_schema_split.txt

State instance (all cases unless noted):
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

### implied_type_nil_object.go

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

        ### Field Report: Investigating Identity Decoding Behavior

**Command 1: Simulated Decode Operation (Case A)**
```
# Input state:
StateInstance{
  AttrsJSON:          `{"id":"foo","foo":"bar"}`,
  IdentityJSON:       `{"id": "foo"}`,
  IdentitySchemaVersion: 0,
  Status:             "ready"
}

# Input schema (Case A):
ProviderSchema{
  Body: &Block{Attributes: {"id": computed string, "foo": optional/computed string}},
  Identity: nil,
  IdentityVersion: 0
}

# Execute Decode()
```
**Observation 1: Failure during unmarshaling**
```
Error: failed to decode identity: unsupported attribute "id". 
This is most likely a bug in the Provider, providers must not change the identity schema without updating the identity schema version
```

**Analysis of Failure Path:**
1. `IdentityJSON != nil` → Enters branch
2. `schema.Identity.ImpliedType()` returns `cty.EmptyObject` (via `specType()` on nil receiver)
3. `ctyjson.Unmarshal()` attempts to decode `{"id":"foo"}` into empty object type
4. Fails because empty object expects no attributes

**Command 2: Compare with Known Working Case (Case B)**
```
# Same state input
# Schema (Case B):
ProviderSchema{
  Body: same as Case A,
  Identity: &Object{Attributes: {"id": required string}, Nesting: NestingSingle},
  IdentityVersion: 0
}

# Execute Decode()
```
**Observation 2: Successful Decode**
```
ResourceInstanceObject{
  Value:    {id: "foo", foo: "bar"},  // (cty object)
  Identity: {id: "foo"},              // (cty object)
  Status:   "ready"
}
```

**Command 3: Test Null IdentityJSON Path (Case C)**
```
# Modified state input:
IdentityJSON: nil

# Schema (Case A):
ProviderSchema{Identity: nil}

# Execute Decode()
```
**Observation 3: Successful Decode with Null Identity**
```
ResourceInstanceObject{
  Value:    {id: "foo", foo: "bar"},
  Identity: cty.NullVal(cty.EmptyObject),
  Status:   "ready"
}
```

**Key Findings:**
1. **Decode produces error** when both:
   - `IdentityJSON != nil`
   - `schema.Identity == nil`
2. Error matches "unsupported attribute" class from `identity type mismatch` test
3. Behavior differs fundamentally from:
   - Case B (produces concrete identity object)
   - Case C (produces typed null)
4. Failure occurs at JSON-to-cty conversion layer when target type is empty object

**Operational Conclusion:**  
For leftover `IdentityJSON` against nil identity schema, `Decode()` does **not** produce a usable identity. It fails with provider contract violation error identical to schema mismatch cases. This occurs because:
- The nil schema's `ImpliedType()` returns `cty.EmptyObject`
- Non-empty JSON cannot unmarshal into empty object type
- Error handling branch treats this as unrecoverable provider incompatibility

**Recommended Next Investigation:**  
Verify provider upgrade/downgrade sequence that could leave `IdentityJSON` populated while current provider reports nil identity schema. The error message explicitly prohibits this schema transition pattern.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
