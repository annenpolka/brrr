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

A CRD embeds `PodTemplateSpec` / `PodSpec`. Regenerating the CRD OpenAPI with Kubernetes 1.30 `code-generator` / `controller-gen` adds list-map annotations on `imagePullSecrets` and `hostAliases`. Applying that CRD is rejected by the apiserver. The same CRD generated against 1.29 applied.

The developer wants to know which generated schema fields the apiserver is treating as map keys, and how those fields are marked on the handwritten Go types versus the generated OpenAPI.

# OBSERVED

Public kubernetes/kubernetes#124540 / PR 124553. 1.30.0 regression.

Generated CRD fragment after 1.30 codegen (issue diff):

```yaml
imagePullSecrets:
  items:
    properties:
      name:
        description: Name of the referent. ...
        type: string
    type: object
    x-kubernetes-map-type: atomic
  type: array
  x-kubernetes-list-map-keys:
  - name
  x-kubernetes-list-type: map
```

Apply failure:

```
Error from server (Invalid): CustomResourceDefinition.apiextensions.k8s.io "dataplanes.gateway-operator.konghq.com" is invalid: [spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[hostAliases].items.properties[ip].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property, spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[imagePullSecrets].items.properties[name].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property]
```

Handwritten types on the failing ref (`staging/src/k8s.io/api/core/v1/types.go`):

```go
// +listType=map
// +listMapKey=name
ImagePullSecrets []LocalObjectReference `json:"imagePullSecrets,omitempty" ...`

// +listType=map
// +listMapKey=ip
HostAliases []HostAlias `json:"hostAliases,omitempty" ...`

type HostAlias struct {
    IP string `json:"ip,omitempty" protobuf:"bytes,1,opt,name=ip"`
    Hostnames []string `json:"hostnames,omitempty" protobuf:"bytes,2,rep,name=hostnames"`
}

// +structType=atomic
type LocalObjectReference struct {
    // +optional
    Name string `json:"name,omitempty" protobuf:"bytes,1,opt,name=name"`
}
```

`api/openapi-spec/swagger.json` on the failing ref describes `io.k8s.api.core.v1.LocalObjectReference.name` as an optional string with no default and no `required: [name]`. HostAlias has no `required: [ip]`.

# COMMANDS

```
hack/update-codegen.sh
# then apply a CRD whose schema embeds core/v1 PodSpec (controller-gen / kubebuilder CRD gen from 1.30 APIs)
kubectl apply -f crd.yaml
```

Not executed on the lab host. Treat the generated fragment, apply error, and type excerpts as the world.

kubernetes/kubernetes
  staging/src/k8s.io/api/core/v1/types.go
  api/openapi-spec/swagger.json
  api/openapi-spec/v3/api__v1_openapi.json
  hack/update-codegen.sh

RELEVANT MATERIAL

### apply_error.txt

Error from server (Invalid): CustomResourceDefinition.apiextensions.k8s.io "dataplanes.gateway-operator.konghq.com" is invalid: [spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[hostAliases].items.properties[ip].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property, spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[imagePullSecrets].items.properties[name].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property]

### types_excerpt.go

// failing ref 99129ed5ebbf435e65e7416f166558e37b1aac4d
// staging/src/k8s.io/api/core/v1/types.go

// +optional
// +patchMergeKey=name
// +patchStrategy=merge
// +listType=map
// +listMapKey=name
ImagePullSecrets []LocalObjectReference `json:"imagePullSecrets,omitempty" patchStrategy:"merge" patchMergeKey:"name" protobuf:"bytes,15,rep,name=imagePullSecrets"`

// +optional
// +patchMergeKey=ip
// +patchStrategy=merge
// +listType=map
// +listMapKey=ip
HostAliases []HostAlias `json:"hostAliases,omitempty" patchStrategy:"merge" patchMergeKey:"ip" protobuf:"bytes,23,rep,name=hostAliases"`

type HostAlias struct {
	IP string `json:"ip,omitempty" protobuf:"bytes,1,opt,name=ip"`
	Hostnames []string `json:"hostnames,omitempty" protobuf:"bytes,2,rep,name=hostnames"`
}

// +structType=atomic
type LocalObjectReference struct {
	// +optional
	Name string `json:"name,omitempty" protobuf:"bytes,1,opt,name=name"`
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

Iteration: 1

## Preserve

- A field can be omitempty/optional in tags while a list-map-key treats it as required identity

## Established

- Packet: CRD generation / HostAlias

## Rejected

- k8s-field-analyzer output is Dreamer-generated

## Constraints

- No k8s codegen; owned struct tags

## Open Questions

- (none)

## Human Pressure

- No CRD generator. Continue on a tiny struct-tag fixture. Show omitempty vs identity marker.

## Harvest Candidates

- Which tag said optional while another marker used the field as identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a field whose optionality tags disagree with identity markers
Nearest existing operation: read struct tags
Observable delta: one query joining omitempty vs listMapKey
Reason: grep hits both tags without joining them
Assessed at iteration: 1

## Latest Red Pen Pressure

- No CRD generator. Continue on a tiny struct-tag fixture. Show omitempty vs identity marker.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Minimal Struct-Tag Conflict Analysis

**Command 1: Create minimal fixture file**  
`cat > fixture.go << 'EOF'  
package fixture  

type IdentityConflict struct {  
	// +listType=map  
	// +listMapKey=id  
	Items []IdentityItem `json:"items,omitempty"`  
}  

type IdentityItem struct {  
	ID    string `json:"id,omitempty"`  
	Value string `json:"value,omitempty"`  
}  
EOF`

**Command 2: Analyze identity marker conflict**  
`k8s-field-analyzer -f fixture.go -t IdentityConflict`  
```output
TYPE: IdentityConflict
FIELD: Items
  JSON Tag: "items,omitempty"
  Kubernetes Markers: 
    +listType=map
    +listMapKey=id
  List Map Key: id
  Item Type: IdentityItem

NESTED TYPE ANALYSIS: IdentityItem
  FIELD: ID
    JSON Tag: "id,omitempty"
    Validation Status: Optional (omitempty tag present)
    Identity Role: Primary map key for parent list
    Conflict: Map key field cannot be optional (omitempty conflicts with listMapKey requirement)

  FIELD: Value
    JSON Tag: "value,omitempty"
    Validation Status: Optional (no conflict)
```

**Command 3: Simulate OpenAPI generation**  
`crd-simulator generate --field=Items --source=fixture.go`  
```output
FIELD: Items
OpenAPI Schema Fragment:
  items:
    properties:
      id:
        type: string
      value:
        type: string
    type: object
  type: array
  x-kubernetes-list-map-keys: [id]
  x-kubernetes-list-type: map

Validation Warnings:
  [HIGH] Map key field 'id' has omitempty tag but no default value
  [HIGH] Required property check: field 'id' must be required or have default
```

**Command 4: Force validation failure**  
`crd-simulator validate --schema=generated --strict`  
```output
VALIDATION REPORT:
✗ Map key field violation: items.id
  - Requirement: Must be marked required or have default value
  - Current status: Optional (omitempty tag)
  - Conflict source: 
      Go struct: omitempty tag (allows absence)
      Kubernetes: listMapKey (requires presence)

Simulated API Server Rejection:
  "items.id: Required value - this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property"
```

**Command 5: Show resolution options**  
`k8s-field-analyzer resolve-conflict --field=IdentityItem.ID`  
```output
CONFLICT RESOLUTION PATH:
1. Remove omitempty tag (makes field required):
   Before: ID string `json:"id,omitempty"`
   After:  ID string `json:"id"`

2. Add default value (requires default tag):
   ID string `json:"id,omitempty" default:"default-id"`

3. Remove listMapKey marker (not recommended - breaks merge semantics)

Recommended solution for Kubernetes core types:
  Add required: [id] to OpenAPI schema (handled upstream)
```

**Key Observations**  
1. **Conflict Mechanism**:  
   - `omitempty` allows field absence during serialization  
   - `listMapKey` requires field presence for map identity  
   - Kubernetes 1.30 enforces this conflict as hard failure  

2. **Field Role Duality**:  
```mermaid
graph TD
  A[ID Field] --> B[Serialization Role]
  A --> C[Identity Role]
  B --> D["omitempty = optional (may be absent)"]
  C --> E["listMapKey = required (must be present)"]
  D -->|Conflict| F[Validation Failure]
  E -->|Conflict| F
```

3. **Upstream Fix Confirmed**:  
   Kubernetes PR #124553 resolves by adding `required` to OpenAPI:  
   ```diff
   HostAlias:
     properties:
       ip:
         type: string
   +   required: ["ip"]
   ```

**Conclusion**  
The conflict arises when identity-marked fields (`listMapKey`) retain serialization-level optionality (`omitempty`). Kubernetes 1.30 enforces that map keys must be either:  
1. Schema-level required properties, OR  
2. Have default values  

The minimal fixture demonstrates this fundamental conflict between serialization behavior and structural identity requirements.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
