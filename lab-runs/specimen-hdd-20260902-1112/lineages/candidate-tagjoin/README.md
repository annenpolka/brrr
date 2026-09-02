# tagjoin

Name a field whose optionality tags disagree with identity markers.

A list can carry `// +listMapKey=ip` while the element field is
`json:"ip,omitempty"` (and maybe `// +optional`). Grep hits both tags.
This command joins them and names the field.

This is an owned Go / comment-tag fixture, not Kubernetes codegen.

## Usage

```
tagjoin FILE.go
tagjoin FILE.go FILE.yaml
tagjoin --check FILE.go
tagjoin < FILE.go
```

`--check` exits 1 on `disagree`, `missing`, or `collision`. `--allow-missing` keeps missing from failing a check. Each path is parsed on its own, then joins merge (`FILE.go FILE.yaml` keeps both).

## Output

Tab-separated rows, one per list-map key, then counts.

```
disagree	HostAlias.IP	list	HostAliases	list_json	hostAliases,omitempty	elem	HostAlias	field	IP	json	ip,omitempty	optional	omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
other_omitempty	HostAlias.Hostnames
disagree_n	2
agree_n	0
missing_n	0
```

| column | meaning |
| --- | --- |
| kind | `disagree`, `agree`, `missing`, `collision`, or `unparsed` |
| `Elem.Field` | identity field on the element type |
| `list` | Go field that carries `+listMapKey` |
| `list_json` | json tag on that list field (often omitempty too) |
| `json` | json tag on the identity field |
| `optional` | `+optional` and/or `omitempty` on the identity field, or `-` |
| `protobuf` | `opt` when the identity field's protobuf tag says opt, else `-` |
| `identity` | `listMapKey` and `patchMergeKey` when present |
| `other_omitempty` | omitempty fields that are not list-map keys |

Identity is the **json wire name**, case-sensitive. `listMapKey=IP` vs
`json:"ip"` is `missing`. Untagged `Name` vs `listMapKey=name` is
`missing` (wire name `Name`). `json:",omitempty"` is an empty json name:
the Go field name is the wire name and omitempty applies (`disagree` when
the key is that Go name). `json:"-"` is not a key. `json:"address"` does
not satisfy `listMapKey=ip`. `json:"inner,inline"` does not flatten.

`disagree` is a list-map key that is optional and has no default.
`agree` is required, or optional with `+default` / YAML `default`.
`missing` is a key that is not a json name on the element type.
`collision` is two fields sharing that json name, or two `type` blocks
with the same name. Anonymous / `json:",inline"` embeds flatten into the
element type (`HostAlias` embedding `Base` still names `HostAlias.IP`).
An untagged slice field still joins. A file that contains `+listMapKey`
or `x-kubernetes-list-map-keys` but yields no join is `unparsed` (exit 2),
not `join none`. Spaces around `+listMapKey = name` and a UTF-8 BOM are
stripped. `/* +listMapKey */` is unparsed, not a silent agree.

Optionality axes:

| signal | verdict |
| --- | --- |
| json `omitempty` / `omitzero` | optional |
| `+optional`, `+kubebuilder:validation:Optional` | optional |
| protobuf `opt` | printed, **not** a verdict |
| `+default`, `+kubebuilder:default` | satisfies identity (`agree`) |
| YAML `required` | required (`agree`) |
| YAML `default` | satisfies identity (`agree`) |

The list field's own `omitempty` is not the join. `agree-name.go` has
`json:"items,omitempty"` on the list and a required `name` key: verdict is
`agree` on `Item.Name`.

## Example (specimen-052)

```
tagjoin fixtures/052-types.go
```

Names `LocalObjectReference.Name` and `HostAlias.IP`. Both are list-map
keys and both are omitempty. `Name` also has `+optional`.

## Boundary

Does not generate CRDs or talk to a cluster. Parses struct tags,
`// +marker` comments, JSON objects, and a YAML indent subset of
`x-kubernetes-list-map-keys` plus item-level `required` / `default`.
`description: |-` and `versions: - name: v1` nested maps stay in the
tree. Local `$ref` is followed; unresolved `$ref` is `unparsed`, not a
false `disagree`. Apply-error text that names
`properties[list].items.properties[key]` in `x-kubernetes-list-map-keys`
is the same join. Duplicate `+listMapKey` lines count once.
