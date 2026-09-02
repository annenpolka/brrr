# Transfer: tagjoin list-map vs optionality onto unseen CRD / OpenAPI

Date: 2026-09-02 15:41 JST
RUN_ID: specimen-hdd-20260902-1112
CLI: `lineages/candidate-tagjoin/tagjoin` sha256 `94bb2f42350c40bf89f50ed63e72fe57d5b5e6017f9031ad08b4180f73f146b8` (KEEP after `destroyers/DESTROYER_tagjoin_2.md`). Host-executed `python3 tagjoin FILE`. No kubectl. No cluster apply. Inputs are not `fixtures/crd-list-map.yaml` and not fixture Go files. Scratch: `destroyers/_tagjoin_transfer_scratch/`.

The join under test: name a list-map identity key whose optionality disagrees (optional, no default). YAML path is `x-kubernetes-list-map-keys` vs OpenAPI `required` / `default`. Go path is `+listMapKey` vs json `omitempty` / `+optional`.

## Control (owned fixture YAML, not the transfer)

```
python3 lineages/candidate-tagjoin/tagjoin lineages/candidate-tagjoin/fixtures/crd-list-map.yaml
```

stdout:

```
disagree	imagePullSecrets.name	list	imagePullSecrets	list_json	imagePullSecrets	elem	imagePullSecrets	field	name	json	name	optional	not-required	protobuf	-	identity	x-kubernetes-list-map-keys
disagree	hostAliases.ip	list	hostAliases	list_json	hostAliases	elem	hostAliases	field	ip	json	ip	optional	not-required	protobuf	-	identity	x-kubernetes-list-map-keys
other_omitempty	none
disagree_n	2
agree_n	0
missing_n	0
collision_n	0
unparsed_n	0
```

rc=0. Indent-subset YAML still joins the owned fragment.

## Input 1: unseen CRD YAML (`x-kubernetes-list-map-keys`)

Downloaded CRDs (not invented, not applied):

| file | source | bytes | list-map hits | sha256 |
| --- | --- | ---: | ---: | --- |
| `kubernetes.crossplane.io_objects.yaml` | crossplane-contrib/provider-kubernetes `main` `package/crds/…` | 39962 | 2 | `e67b823e427dee4c03630ddc749b5bf9b768a317bf806927be2963a0a2a6df94` |
| `px.dev_viziers.yaml` | pixie-labs/pixie `main` `k8s/operator/crd/base/…` | 18067 | 1 | `d9d1deacc7cb004b831537aa28289a44e231bfc6a2bfde668c2351f8576f3278` |
| `monitoring.coreos.com_servicemonitors.yaml` | prometheus-operator `main` example CRD | 74781 | 2 | `7dd4206947c94bc76f71daa07c45a1010a5d697c54fe079f8207b0e82026a26a` |
| `gateway.networking.k8s.io_httproutes.yaml` | kubernetes-sigs/gateway-api `main` standard CRD | 429304 | 22 | `5b746e5dd696239cdf7d1a6dc6293d103fb78056598aa3f2e14f7512dc8c362b` |
| `cert-manager.io_certificates.yaml` | cert-manager v1.15.3 `cert-manager.crds.yaml` | 583245 | 4 | `c5d8af8853257118bcfd9b4e665a1dae538065bf9b895f98ceb08751f90aebb7` |

Those files contain real keys the fixture never named (`conditions.type`, pixie `claims.name`, ServiceMonitor `group`/`resource`/`name`/`namespace`, HTTPRoute header `name`). Several of those keys are in `required` (would be `agree` if walked). Crossplane `conditions` still has `description: |-` prose above `x-kubernetes-list-map-keys: [type]`.

```
python3 lineages/candidate-tagjoin/tagjoin destroyers/_tagjoin_transfer_scratch/kubernetes.crossplane.io_objects.yaml
```

stdout (identical on pixie, ServiceMonitor, HTTPRoute, cert-manager CRDs):

```
unparsed	x-kubernetes-list-map-keys
other_omitempty	none
disagree_n	0
agree_n	0
missing_n	0
collision_n	0
unparsed_n	1
```

rc=2. `--check` on the Crossplane CRD is also rc=2 (unparsed, not a disagree).

Walker diagnostic (host, `load_yaml_subset` on pixie): tree top keys are only `apiVersion` / `kind` / `metadata` / `spec`; 6 walk nodes; 0 `x-kubernetes-list-map-keys` nodes. The indent subset treats `description: |-` as a scalar and then `break`s the parent map on the following indented prose, so the list-map node is never in the tree. Hint string is still in the file, so the CLI refuses `join none` and prints `unparsed`. Same miss on extracted real subtrees that still contain `|-`.

Argo CD `application-crd.yaml` has **zero** `x-kubernetes-list-map-keys` hits → `join none` rc=0 (no identity hint; not this miss).

Result: **MISS (unparsed)** on unseen CRD YAML.

## Input 2: unseen OpenAPI JSON

```
python3 lineages/candidate-tagjoin/tagjoin destroyers/_tagjoin_transfer_scratch/apis__apps__v1_openapi.json
```

Source: kubernetes/kubernetes `v1.30.0` `api/openapi-spec/v3/apis__apps__v1_openapi.json` (827632 bytes, 24 `x-kubernetes-list-map-keys` hits).

stdout:

```
unparsed	x-kubernetes-list-map-keys
other_omitempty	none
disagree_n	0
agree_n	0
missing_n	0
collision_n	0
unparsed_n	1
```

rc=2. JSON quoted keys are not the indent-YAML walker’s map keys.

Result: **MISS (unparsed)** on OpenAPI JSON.

## Input 3: second Go types file (not in fixtures)

```
python3 lineages/candidate-tagjoin/tagjoin destroyers/_tagjoin_transfer_scratch/k8s-core-v1-types.go
```

Source: kubernetes/kubernetes `v1.30.0` `staging/src/k8s.io/api/core/v1/types.go` (394093 bytes, 35 `+listMapKey` hits, sha256 `e2ffda7c3e2439246f323540e5ab62166de96fbe5c0d92ce5f52a9a3e41dc4d2`). This is the types file behind specimen-052, not the owned excerpt.

Disagree / missing rows (stdout TSV; `other_omitempty` omitted — one fat line):

```
disagree	LocalObjectReference.Name	list	ImagePullSecrets	list_json	imagePullSecrets,omitempty	elem	LocalObjectReference	field	Name	json	name,omitempty	optional	+optional,omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
disagree	HostAlias.IP	list	HostAliases	list_json	hostAliases,omitempty	elem	HostAlias	field	IP	json	ip,omitempty	optional	omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
disagree	PodIP.IP	list	PodIPs	list_json	podIPs,omitempty	elem	PodIP	field	IP	json	ip,omitempty	optional	omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
missing	Condition.type	list	Conditions	list_json	conditions,omitempty	elem	Condition	field	type	json	-	optional	-	protobuf	-	identity	listMapKey,patchMergeKey
disagree	ObjectReference.Name	list	Secrets	list_json	secrets,omitempty	elem	ObjectReference	field	Name	json	name,omitempty	optional	+optional,omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
disagree_n	4
agree_n	25
missing_n	1
collision_n	0
unparsed_n	0
```

rc=0. `--check` rc=1 (the four disagrees plus missing). Required keys (`EnvVar.Name`, `ContainerPort.ContainerPort`, `VolumeMount.MountPath`, …) are `agree`. List-field omitempty is still not the join. `Condition.type` is `missing` (metav1.Condition lives in another file). `HostAlias.Hostnames` remains `other_omitempty`, not a list-map key.

Result: **TRANSFER** on unseen Go types.go. Same two specimen-052 disagrees, plus `PodIP.IP` and ServiceAccount `ObjectReference.Name`.

## Verdict

**CRD / OpenAPI YAML: MISS (unparsed, rc=2).** Real CRDs and swagger JSON contain `x-kubernetes-list-map-keys` and the CLI does not silently print `join none`, but it also does not name which key is optional. The indent YAML walker does not survive `description: |-` (documented leftover in `MUTATE.md`).

**Go types (not in fixtures): TRANSFER.** The list-map vs optionality join names `LocalObjectReference.Name` and `HostAlias.IP` on the real v1.30.0 types file.

Do not treat the YAML miss as a KILL of the Go join. Do not invent kubectl apply.
