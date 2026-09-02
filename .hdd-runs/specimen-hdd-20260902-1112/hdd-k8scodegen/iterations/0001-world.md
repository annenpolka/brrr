# Current situation

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
