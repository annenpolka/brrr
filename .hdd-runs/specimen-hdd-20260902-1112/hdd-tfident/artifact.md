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
