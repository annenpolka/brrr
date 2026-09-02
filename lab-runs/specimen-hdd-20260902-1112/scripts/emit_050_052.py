#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packets specimen-050..052."""
from __future__ import annotations

from emit_specimen import emit

PACKETS = []


def add(**kwargs):
    PACKETS.append(kwargs)


add(
    id="specimen-050",
    manifest="""
id: specimen-050
kind: REAL_SOURCE_BACKED
repository: serde-rs/serde
failing_ref: 58a8d229315553c4ae0a8d7eee8e382fbae4b4bf
fixed_ref: c17b139a266c89fddec91a6151b442d985bc735a
source_pr: https://github.com/serde-rs/serde/pull/2786
mechanism_tags:
  - serialization-format-boundary
  - flatten-enum
  - roundtrip-asymmetry
ecosystem: rust
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A struct flattens an externally tagged enum. One variant is a unit variant.

JSON `{"Unit":null}` deserializes into that struct. Serializing the resulting value fails.

The developer wants to know which direction of the format boundary accepted the unit variant, which direction rejected it, and what token sequence each side actually produced.
""",
    observed="""# OBSERVED

Public serde-rs/serde PR 2786 (failing world around serde 1.0.204 / serde_json 1.0.121). Playground shape used in the report:

```rust
use serde::{Deserialize, Serialize};
use serde_json::{from_str, to_string};

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Flatten {
    #[serde(flatten)]
    data: Enum,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
enum Enum {
    Unit,
}

const JSON: &str = r#"{"Unit":null}"#;

#[test]
fn de() {
    assert_eq!(from_str::<Flatten>(JSON).unwrap(), Flatten { data: Enum::Unit });
}

#[test]
fn ser() {
    assert_eq!(to_string(&Flatten { data: Enum::Unit }).unwrap(), JSON);
}
```

On the failing revision:

- `de` passes.
- `ser` panics: `called Result::unwrap() on an Err value: Error("can only flatten structs and maps (got an enum)", line: 0, column: 0)`.

Sibling flatten cases already in `test_suite/tests/test_annotations.rs` (`mod flatten` / `mod enum_`) cover Newtype / Tuple / Struct variants and round-trip those. The unit variant is absent from that enum on the failing ref.

In-tree serde flatten serializer on the failing ref (`serde/src/private/ser.rs`, `FlatMapSerializer::serialize_unit_variant`) takes the unit-variant call and returns the flatten-type error above. Newtype-variant flattening already writes a map entry.
""",
    commands="""# COMMANDS

```
cargo test -p serde --test test_annotations flatten::enum_ -- --nocapture
# user snippet (not in-tree on the failing ref):
# cargo test --test flatten_roundtrip
```

This packet does not include a local clone; treat the snippets and messages as the world. Do not execute untrusted checkouts on the host.
""",
    tree="""serde-rs/serde
  serde/src/private/ser.rs
  test_suite/tests/test_annotations.rs
""",
    source="""repository: serde-rs/serde
pr: https://github.com/serde-rs/serde/pull/2786
failing_ref (PR base at open): 58a8d229315553c4ae0a8d7eee8e382fbae4b4bf
fixed_ref (PR head commit): c17b139a266c89fddec91a6151b442d985bc735a
merged_at: 2024-12-27T08:24:29Z
merged_by: oli-obk
""",
    answer_key="""KNOWN FIX (sealed): serde PR 2786. FlatMapSerializer.serialize_unit_variant ignored the variant identifier and returned Unsupported::Enum, while flatten deserialize already treated a unit variant as a map key whose value is null. Repair writes serialize_entry(variant, unit-value) and cfg-gates the Enum unsupported arm to no_std/no_alloc only. In-tree regression: flatten::enum_::unit in test_annotations.rs.
Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1
contrastive serialize-fail vs deserialize-pass on one JSON object; multi-step format-boundary diagnosis; user snippet does not name the in-tree flatten serializer.
""",
    files={
        "flatten_roundtrip.rs": """use serde::{Deserialize, Serialize};
use serde_json::{from_str, to_string};

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Flatten {
    #[serde(flatten)]
    data: Enum,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
enum Enum {
    Unit,
}

const JSON: &str = r#"{"Unit":null}"#;

#[test]
fn de() {
    assert_eq!(from_str::<Flatten>(JSON).unwrap(), Flatten { data: Enum::Unit });
}

#[test]
fn ser() {
    // failing revision: Error("can only flatten structs and maps (got an enum)", line: 0, column: 0)
    assert_eq!(to_string(&Flatten { data: Enum::Unit }).unwrap(), JSON);
}
""",
    },
)

add(
    id="specimen-051",
    manifest="""
id: specimen-051
kind: REAL_SOURCE_BACKED
repository: gradle/gradle
failing_ref: 534cde90a908ee201352ad834eb37ead2dfd0e24
fixed_ref: 2f4713e0fe1d7b56e0d7284f1e546bdccf2a102a
source_issue: https://github.com/gradle/gradle/issues/32828
source_pr: https://github.com/gradle/gradle/pull/37818
mechanism_tags:
  - serialization-deadlock
  - configuration-cache
  - nested-identity
ecosystem: java
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

An extension constructs a `ValueSource` provider. The source parameters are a `@Nested` bean that is the same nested object the extension already exposes. The extension stores that provider and a task takes it as `@Input`.

With configuration cache enabled, the first run stores the cache and prints the expected value. The second run, recovering from the cache, hangs until a timeout rather than loading.

If the nested bean is created separately from the extension that owns the provider, both store and load complete.

The developer wants to know which objects were being written and read as shared, and which wait never completed during load.
""",
    observed="""# OBSERVED

Public gradle/gradle#32828 / PR 37818. Gradle 8.11 report. External repro: https://github.com/lukebemish/gradle-issue-32828

Shape from the issue (Java):

```java
public abstract class A {
    public abstract static class B {}

    public abstract static class Params implements ValueSourceParameters {
        @Nested
        public abstract Property<B> getB();
    }

    public abstract static class V implements ValueSource<String, Params> {}

    private final Provider<String> calculated;

    @Inject
    public A(ProviderFactory providers) {
        var source = providers.of(V.class, it -> {
            it.getParameters().getB().set(getB());
        });
        this.calculated = source;
    }

    @Nested
    public abstract B getB();

    public Provider<String> getCalculated() {
        return calculated;
    }
}
```

Observed:

- First invocation with configuration cache: store succeeds; task output is the obtained value.
- Second invocation: configuration cache load does not finish; process waits until a one-minute wait on a shared-object future, then fails with a timeout while waiting for a value.
- Decoupling construction of `B` from the containing extension removes the hang.
- PR integration test (`ConfigurationCacheValueSourceIntegrationTest`) encodes the same graph in Groovy: extension `A` with nested `B`, `providers.of(MySrc)` whose params hold `B`, task input is the calculated provider. On the failing revision that test hangs on the load half.
""",
    commands="""# COMMANDS

```
./gradlew show --configuration-cache
./gradlew show --configuration-cache   # second run: load hangs / times out on failing revision
```

Focused in-tree names on the PR:

```
:configuration-cache:embeddedIntegTest --tests org.gradle.internal.cc.impl.ConfigurationCacheValueSourceIntegrationTest
```

Not executed on the lab host. Treat the snippets and timeout as the world.
""",
    tree="""gradle/gradle
  platforms/core-configuration/configuration-cache/src/integTest/groovy/org/gradle/internal/cc/impl/ConfigurationCacheValueSourceIntegrationTest.groovy
  platforms/core-configuration/core-serialization-codecs/src/main/kotlin/org/gradle/internal/serialize/codecs/core/ProviderCodecs.kt
  platforms/core-configuration/configuration-cache/src/main/kotlin/org/gradle/internal/cc/impl/serialize/DefaultSharedObjectCodec.kt
  platforms/core-configuration/model-core/src/main/java/org/gradle/api/internal/provider/DefaultValueSourceProviderFactory.java
""",
    source="""repository: gradle/gradle
issue: https://github.com/gradle/gradle/issues/32828
pr: https://github.com/gradle/gradle/pull/37818
reproducer: https://github.com/lukebemish/gradle-issue-32828
failing_ref (PR base at open): 534cde90a908ee201352ad834eb37ead2dfd0e24
fixed_ref (PR head commit): 2f4713e0fe1d7b56e0d7284f1e546bdccf2a102a
pr_commits:
  - e2a3ac8e405e07877ae38032d650191bce9b0e04
  - f6ff94cb156dd293a8a60419ccd9cc62f49b8e2d
  - 19daf59f7757c89b63b71dbbed1147631ab99090
  - 2f4713e0fe1d7b56e0d7284f1e546bdccf2a102a
merged_at: 2026-06-09T18:17:08Z
merged_by: ov7a
""",
    answer_key="""KNOWN FIX (sealed): gradle PR 37818. ValueSourceProviderCodec decoded nested parameters before the provider was present in sharedIdentities, so a nested bean that referred back at the provider made DefaultSharedObjectDecoder's reader thread wait on its own FutureValue latch until the one-minute timeout. Repair: instantiate the provider first with late-bound parameters, register identity, then decode parameters; decoder detects reader-thread self-wait, records readFailure, and releases remaining latches when the reader stops.
Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1
contrastive hang-on-load vs pass-when-nested-bean-is-decoupled; timeout rather than a named cycle; multi-step serialization diagnosis.
""",
    files={
        "ExtensionA.java": """public abstract class A {
    public abstract static class B {}

    public abstract static class Params implements ValueSourceParameters {
        @Nested
        public abstract Property<B> getB();
    }

    public abstract static class V implements ValueSource<String, Params> {}

    private final Provider<String> calculated;

    @Inject
    public A(ProviderFactory providers) {
        var source = providers.of(V.class, it -> {
            it.getParameters().getB().set(getB());
        });
        this.calculated = source;
    }

    @Nested
    public abstract B getB();

    public Provider<String> getCalculated() {
        return calculated;
    }
}
""",
    },
)

add(
    id="specimen-052",
    manifest="""
id: specimen-052
kind: REAL_SOURCE_BACKED
repository: kubernetes/kubernetes
failing_ref: 99129ed5ebbf435e65e7416f166558e37b1aac4d
fixed_ref: 5777fd493946e71880e2de556d02632521c0a652
source_issue: https://github.com/kubernetes/kubernetes/issues/124540
source_pr: https://github.com/kubernetes/kubernetes/pull/124553
mechanism_tags:
  - generated-code-drift
  - openapi-crd
  - list-map-keys
ecosystem: go
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 8000
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

A CRD embeds `PodTemplateSpec` / `PodSpec`. Regenerating the CRD OpenAPI with Kubernetes 1.30 `code-generator` / `controller-gen` adds list-map annotations on `imagePullSecrets` and `hostAliases`. Applying that CRD is rejected by the apiserver. The same CRD generated against 1.29 applied.

The developer wants to know which generated schema fields the apiserver is treating as map keys, and how those fields are marked on the handwritten Go types versus the generated OpenAPI.
""",
    observed="""# OBSERVED

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
""",
    commands="""# COMMANDS

```
hack/update-codegen.sh
# then apply a CRD whose schema embeds core/v1 PodSpec (controller-gen / kubebuilder CRD gen from 1.30 APIs)
kubectl apply -f crd.yaml
```

Not executed on the lab host. Treat the generated fragment, apply error, and type excerpts as the world.
""",
    tree="""kubernetes/kubernetes
  staging/src/k8s.io/api/core/v1/types.go
  api/openapi-spec/swagger.json
  api/openapi-spec/v3/api__v1_openapi.json
  hack/update-codegen.sh
""",
    source="""repository: kubernetes/kubernetes
issue: https://github.com/kubernetes/kubernetes/issues/124540
pr: https://github.com/kubernetes/kubernetes/pull/124553
failing_ref (PR base at open): 99129ed5ebbf435e65e7416f166558e37b1aac4d
fixed_ref (PR head commit): 5777fd493946e71880e2de556d02632521c0a652
pr_commits:
  - a2d4f5b00958637b01524a03c08296d443e71f9c
  - 29bff5f8dd530a3f24b7c9dc849472f7f57e5de8
  - 3ecbfed8e60902e6fd5d02fc3f092f92d8b2e5b6
  - e523b705ca94af5563750208bbd208fb772846fa
  - 5777fd493946e71880e2de556d02632521c0a652
merged_at: 2024-05-03T22:21:15Z
merged_by: k8s-ci-robot
milestone: v1.31
""",
    answer_key="""KNOWN FIX (sealed): kubernetes PR 124553. 1.30 codegen emitted x-kubernetes-list-map-keys name/ip for imagePullSecrets and hostAliases, but LocalObjectReference.Name stayed +optional without a default and HostAlias.IP stayed omitempty/unrequired, so CRD admission rejected the generated OpenAPI. Repair: empty-string default (kubebuilder:default) on Name, required IP on HostAlias, then hack/update-codegen.sh to refresh swagger and v3 OpenAPI specs.
Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1
contrastive 1.29 apply vs 1.30 generated schema rejection; handwritten types vs generated OpenAPI disagree on map-key fields; multi-step codegen diagnosis.
""",
    files={
        "types_excerpt.go": """// failing ref 99129ed5ebbf435e65e7416f166558e37b1aac4d
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
""",
        "apply_error.txt": """Error from server (Invalid): CustomResourceDefinition.apiextensions.k8s.io "dataplanes.gateway-operator.konghq.com" is invalid: [spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[hostAliases].items.properties[ip].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property, spec.validation.openAPIV3Schema.properties[spec].properties[deployment].properties[podTemplateSpec].properties[spec].properties[imagePullSecrets].items.properties[name].default: Required value: this property is in x-kubernetes-list-map-keys, so it must have a default or be a required property]
""",
    },
)


def main() -> None:
    for packet in PACKETS:
        dest = emit(packet)
        print(dest)


if __name__ == "__main__":
    main()
