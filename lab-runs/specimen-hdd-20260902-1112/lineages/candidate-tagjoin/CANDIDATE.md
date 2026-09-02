# tagjoin

origin.method: hdd
origin.trial: hdd-k8scodegen
specimens: [specimen-052]

classification: USEFUL_COMPOSITION

## Primitive

Name a field whose optionality tags disagree with identity markers.

## Why this might not exist

`grep omitempty` and `grep listMapKey` both hit. The miss is the join:
this json name is a list-map key *and* optional, often on the element
type rather than the list field. Reading tags still leaves that as a
hand comparison.

## Core operation

Parse `// +listMapKey=NAME` on a slice field, find `NAME` as the element
type's **json wire name** (case-sensitive; empty json name = Go field
name; `json:"-"` is not a key; no Go-name fallback when a json tag
renamed the field), and report whether that field is optional without a
default. YAML / JSON `x-kubernetes-list-map-keys` / apply-error text is
the same question against item-level OpenAPI `required` / `default`.

## Observable delta

One query joining omitempty vs listMapKey. On the owned fixture,
`HostAlias.IP` and `LocalObjectReference.Name` are `disagree`.

## Reality mapping

Owned Go fixture `fixtures/052-types.go` (and excerpt-style loose fields
in `fixtures/excerpt.go` / specimen-052 `types_excerpt.go`). No codegen.

## Research boundary

Does not rebuild a CRD generator. Does not talk to a cluster. Does not
invent OpenAPI.

## Removed

k8s-field-analyzer, controller-gen, kubectl apply.

## Smallest artifact

Python 3 stdlib CLI `tagjoin`.

## Pre-implementation Reality assessment

See `REALITY.md`. Classification USEFUL_COMPOSITION. Nearest existing
operation: read struct tags. Observable delta: one query joining
omitempty vs listMapKey.

## How to run

From this directory:

```
python3 tests/test_tagjoin.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. Third mutate after TRANSFER_tagjoin_crd.md MISS
(`description: |-` dropped list-map keys) and DESTROYER_tagjoin_2.md KEEP
leftovers (case-fold, FILE.go FILE.yaml, versions sequences).
`./demo.sh` twice (identical). Tests: 52 OK.

Nearest existing (`grep omitempty|listMapKey|+optional`) hits list tags,
`Hostnames`, and the identity keys without joining them.

```
== tagjoin owned wrapped fixture (specimen-052 shape) ==
disagree	LocalObjectReference.Name	list	ImagePullSecrets	list_json	imagePullSecrets,omitempty	elem	LocalObjectReference	field	Name	json	name,omitempty	optional	+optional,omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
disagree	HostAlias.IP	list	HostAliases	list_json	hostAliases,omitempty	elem	HostAlias	field	IP	json	ip,omitempty	optional	omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
other_omitempty	HostAlias.Hostnames
disagree_n	2
agree_n	0
missing_n	0
collision_n	0
unparsed_n	0
```

Specimen-052 `types_excerpt.go` (loose fields, not wrapped in a struct): same
two `disagree` rows.

Unseen `Ports` / `containerPort`: `disagree ContainerPort.ContainerPort`,
`other_omitempty none`.

Agree fixture: list is still `items,omitempty`; key is `json name` with
`optional -`; verdict `agree Item.Name`; `other_omitempty Item.Value`.

## Dogfood

First demo: `grep omitempty` hit the list fields (`imagePullSecrets,omitempty`,
`hostAliases,omitempty`) and `Hostnames` as well as the identity keys. The
join named `LocalObjectReference.Name` and `HostAlias.IP` but still required
a hand look to see that list omitempty ≠ key omitempty. One query now prints
`list_json` next to `json`, `protobuf opt` without using it for verdict, and
`other_omitempty HostAlias.Hostnames`.

## Surprises

Grep's first `+optional` hits are on the *lists* (`ImagePullSecrets`,
`HostAliases`), not on `Name`. List-level `+optional` is not the identity-key
disagreement. `Hostnames` is omitempty and not a list-map key.

Both disagreeing keys also have protobuf `opt`; the agree name key does not.
Verdict still ignores protobuf.

## Failures

Does not parse full Go (generics, nested structs, type aliases). Does not
emit OpenAPI or repair tags. protobuf `opt` is reported, not a verdict.
YAML walker is an indent subset (no anchors / aliases) that keeps
siblings after `|-` and `versions:` sequence children. Duplicate `type`
names are `collision`, not last-wins. Go tags and YAML keys are separate
rows, not one merged HostAlias.IP ↔ hostAliases.ip object. Empty-name
`json:",inline"` embeds and untagged slice fields join; `json:"inner,inline"`
does not flatten. `/* +listMapKey */` is `unparsed`.

## Suggested mutations (applied 2026-09-02)

- `--check` exit 1 on `disagree` / `missing` / `collision`
- Join YAML `x-kubernetes-list-map-keys` with `required` / `default`
- `json:",omitempty"` is empty name + omitempty (`disagree`)
- No Go-name fallback when json renamed the field
- Duplicate `+listMapKey` counts once; duplicate `type` names are collision
- `unparsed` + rc=2 instead of `join none` on identity-shaped text
- `+default` / YAML default satisfies identity; protobuf `opt` still not a verdict
- `json:",inline"` / anonymous embeds flatten; untagged list fields join
- BOM and `+listMapKey = name` are not silent misses
- YAML `description: |-` does not drop `x-kubernetes-list-map-keys`
- `versions:` sequence maps keep nested schema children
- JSON OpenAPI objects join; local `$ref` is followed
- `FILE.go FILE.yaml` parses each path, then merges joins
- Json identity is case-sensitive (`IP` vs `ip` is `missing`)

## Kill / keep

Keep if the owned fixture names `HostAlias.IP` and
`LocalObjectReference.Name` as `disagree` while a required list-map key
is `agree`. Mutation must not restore `agree` on `json:",omitempty"` or
`disagree` on a Go field whose json name is not the list-map key.
