# DESTROYER tagjoin

Date: 2026-09-02 13:30 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin`

Worktree (byte-identical, sha256 `20b2ae10862f8f815f3284590ec3aac2455794de68de6726a1f565d634edc8b5`, 11025 bytes, HEAD `f0171af`): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin/tagjoin/tagjoin`

Origin claim: name the field whose optionality tags disagree with `+listMapKey` identity. `grep omitempty` and `grep listMapKey` both hit; the miss is the join, often on the element type rather than the list field. Specimen-052. Kind: USEFUL_COMPOSITION.

Happy path is real. Unit tests (12/12) pass. `./demo.sh` twice, byte-identical. Owned `fixtures/052-types.go` and specimen-052 `types_excerpt.go` both name `LocalObjectReference.Name` and `HostAlias.IP` as `disagree`, list omitempty is not the join (`agree-name.go` → `agree Item.Name`), unseen `containerPort` transfers. That is not enough. Identity is a Go-name fallback after a broken `json:",omitempty"` parse; `agree` is exit 0 with unsupported certainty; the specimen's actual artifact (`x-kubernetes-list-map-keys` must be required or have a default) is `join none`.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/fixtures
S052=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052
```

No merge onto `main`. No controller-gen, no cluster, no OpenAPI emitter. This object is the omitempty / `+optional` vs `+listMapKey` join in one Go tag file, not kubectl apply.

---

## What still works

The owned wrapped fixture, the loose excerpt, and any other single-file `type T struct` whose list field carries `// +listMapKey=NAME` on its own comment block and whose element type in the same blob has a tagged field whose json name is `NAME`.

```bash
python3 "$CLI" "$FX/052-types.go"
python3 "$CLI" "$S052/files/types_excerpt.go"
python3 "$CLI" "$FX/agree-name.go"
python3 "$CLI" "$FX/unseen-ports.go"
```

```text
disagree	LocalObjectReference.Name	list	ImagePullSecrets	list_json	imagePullSecrets,omitempty	...	json	name,omitempty	optional	+optional,omitempty	protobuf	opt	identity	listMapKey,patchMergeKey
disagree	HostAlias.IP	list	HostAliases	list_json	hostAliases,omitempty	...	json	ip,omitempty	optional	omitempty	protobuf	opt
other_omitempty	HostAlias.Hostnames
disagree_n	2
agree_n	0
missing_n	0
rc=0
```

`agree-name.go`: list is still `items,omitempty`; key is `json name` with `optional -`; verdict `agree Item.Name`; `other_omitempty Item.Value`. `[]*corev1.HostAlias` strips to `HostAlias`. Two `+listMapKey` lines on one field become two rows. `+optional` on the list only is not the join. Stdin, `-`, symlink, FIFO with a writer, `cat list.go elem.go | tagjoin -` (concat as one blob) work.

Unseen k8s-shaped transfers (not in fixtures):

| shape | verdict |
| --- | --- |
| `VolumeMounts` `listMapKey=mountPath`, key `json:"mountPath"` | `agree VolumeMount.MountPath` |
| `Env []EnvVar` `listMapKey=name`, key `json:"name"` | `agree EnvVar.Name`; `other_omitempty EnvVar.Value` |
| Ports `containerPort` + `protocol` | `agree ContainerPort.ContainerPort`; `disagree ContainerPort.Protocol`; `other_omitempty ContainerPort.HostPort` |

Nearest existing (`grep -nE 'omitempty|listMapKey|\+optional'`) hits list tags, `Hostnames`, list-level `+optional`, and the identity keys without naming which identity key is optional. That join is the whole useful delta. Attacks below break identity around it, or show the primitive cannot see the specimen's generated schema.

---

## Implementation

### 1. `json:",omitempty"` is a required key

Standard encoding/json: empty name + `omitempty` means the Go field name is optional. tagjoin splits on comma, drops empties, then treats the first remaining token as the json *name*:

```text
parts[0] == "omitempty"
omit == ("omitempty" in parts[1:]) == False
```

```bash
python3 "$CLI" - <<'GO'
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:",omitempty"`
}
GO
```

```text
agree	Item.Name	...	json	,omitempty	optional	-	...
agree_n	1
other_omitempty	none
rc=0
```

The json column still contains `omitempty`. The optional column is `-`. Verdict is `agree`. The field is also absent from `other_omitempty` because that walk uses the same `json_parts`. Grep hits it; the join calls it required.

`// +listMapKey=omitempty` matches the same field via the invented json name `omitempty`, still `agree`.

### 2. Go-name fallback joins the wrong json identity

`find_key_field` tries json names, then `fld.name.lower() == key.lower()`. CRD list-map keys are json names.

```bash
python3 "$CLI" - <<'GO'
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
GO
```

```text
disagree	HostAlias.IP	...	json	address,omitempty	optional	omitempty
rc=0
```

The list-map key is `ip`. The wire name is `address`. tagjoin reports a disagreement on a property the generated OpenAPI would not use as the map key.

Same fallback: `json:"-"` with `listMapKey=Name` is `agree Item.Name` (the field is omitted from JSON entirely). `listMapKey=IP` vs `json:"ip"` matches via case-fold of the Go name, which happens to be right on HostAlias and would be wrong if a sibling field owned json `ip`.

When both exist, json-name match correctly wins (`Name json:"id"` plus `ID json:"name,omitempty"` → `disagree Item.ID`). The fallback is the hole, not the first pass.

### 3. Duplicate identities: first json name, last type, double count

| input | result |
| --- | --- |
| two fields `json:"name,omitempty"` then `json:"name"` | first wins: `disagree Item.A`; required `B` is invisible |
| two `type HostAlias` (required IP, then omitempty IP) | dict last-wins: `disagree` |
| `// +listMapKey=name` twice on one list | two identical `disagree` rows; `disagree_n 2` |

`disagree_n` is not a count of disagreeing fields. Tests never duplicate a key or a type name.

### 4. Marker grammar is one exact spelling

`MARKER_RE` is `^//\s*\+([A-Za-z][\w-]*)(?:=(\S+))?\s*$`. Anything else is a silent miss (`join none` or `missing`), rc=0.

| spelling | observed |
| --- | --- |
| `// +listMapKey = name` (spaces) | `join none`; `other_omitempty Item.Name` |
| `// +listMapKey=` | `join none` |
| `// +listMapKey=name,port` | `missing Item.name,port` (one token) |
| `/* +listMapKey=ip */` | `join none` |
| `HostAliases ... // +listMapKey=ip` (same line) | `join none` |
| UTF-8 BOM on the marker line | `join none` |
| `// +listMapKey=ip` on the **type**, not the field | `join none` |
| `// +patchMergeKey=ip` only | `join none` |
| `// +listMapKey=ip` then a `var` line then the field | markers cleared; `join none` |
| blank line / `// docs` between marker and field | still attached (blank does not clear) |

`+kubebuilder:validation:Optional` does not match; `json:"name"` → `agree`. `json:"name,omitzero"` → `agree`. `+default=""` next to omitempty → still `disagree` (the apiserver rule is default **or** required).

### 5. The parser is a field-line regex, not Go

`FIELD_RE` requires `Name Type \`tags\``. `TYPE_RE` requires `type Name struct {` on one line.

| Go | observed |
| --- | --- |
| list field with no tags | not a field; `join none` |
| `*[]HostAlias` / `[3]HostAlias` / `map[string]Item` | `missing` with `elem -` |
| `[][]HostAlias` | `missing []HostAlias.ip` |
| `type Alias HostAlias` | `missing Alias.ip` |
| anonymous embed `Base \`json:",inline"\`` | `missing HostAlias.ip`; `other_omitempty Base.IP` |
| `[]struct { Name string \`json:"name,omitempty"\` }` | list not parsed; inner `Name` leaks as `other_omitempty Spec.Name` |
| `type Spec[T any] struct` | `missing T.name` |
| `// +listMapKey=name` on the **element** field | treats `Name string` as a list; `missing -.name` |

Real `k8s.io/api` files use embeds, aliases, and untagged fields. The owned fixtures do not.

Missing file / directory: clean `tagjoin:` rc=1. Invalid UTF-8 / binary: `UnicodeDecodeError` is a `ValueError`, rc=2, no traceback. Garbage text, YAML, `/dev/null`, empty stdin: `join none` rc=0.

### 6. Misleading exit zero; `--check` does not exist

Every successful parse is rc=0, including `disagree`, `missing`, `join none`, YAML CRDs, and `agree` that is false (sections 1–2). CANDIDATE.md listed `--check` exit 1 on `disagree`. Observed:

```bash
python3 "$CLI" --check "$FX/052-types.go"
# argparse rc=2: unrecognized arguments: --check
```

`tagjoin a.go b.go` is the same argparse error. Cross-file only works if the caller concatenates onto stdin.

Pipe: `cut -f1,2` on the happy path is `disagree` / `LocalObjectReference.Name`. A tab inside a json tag splits the row (`json:"na\tme,omitempty"` → extra column). `other_omitempty` is one line of all non-key omitempty names; 2000 structs → 336724 bytes stdout in 0.044s, one TSV field-bomb. `| true` leaves `BrokenPipeError` on flush (ignored, inner rc=0).

### 7. Huge / weird, non-fatal

2000 list+elem pairs: rc=0, 2000 `disagree` rows plus one `other_omitempty` line. NUL in a UTF-8 file still finds `HostAlias.IP`. 5 MB is not required; the 2000-struct case already shows there is no cap and no per-row `other_omitempty`.

---

## Primitive

Reality-stripped operation: line-regex Go-ish tags; collect `+listMapKey` on slice fields; look up that string on the element struct (json name, else Go name); `disagree` iff the target has json `omitempty` or `+optional`.

Nearest ordinary workflow: `grep omitempty` and `grep listMapKey` in one file, then a hand look at whether the key lives on the element type. `list_json` vs `json` and `other_omitempty` are the dogfood labels for that hand look. Observable capability lost if the **CLI** vanishes: naming `HostAlias.IP` and `LocalObjectReference.Name` as the identity keys that are optional, without naming `Hostnames` or the list fields. That join is real.

Lost if the **question** is the specimen's apply error, nothing:

```text
hostAliases.items.properties[ip] ... in x-kubernetes-list-map-keys, so it must have a default or be a required property
imagePullSecrets.items.properties[name] ...
```

```bash
python3 "$CLI" "$S052/files/apply_error.txt"   # join none rc=0
python3 "$CLI" crd.yaml                        # x-kubernetes-list-map-keys: join none rc=0
```

tagjoin never reads generated OpenAPI `required` / `default` / `x-kubernetes-list-map-keys`. It answers a Go-tag proxy. `protobuf opt` is printed and ignored (HostAlias.IP is `agree` if json omitempty is removed and protobuf stays `opt`). `+default=""` does not flip `disagree`. The apiserver rule is not the verdict.

That is why this is not KILL: the *question* (this json name is a list-map key *and* optional, on the element type) is a debugging object grep will not emit. The current embodiment is a specimen-052 comment-tag replay that will `agree` a `json:",omitempty"` key, `disagree` a Go field whose json name is not the key, and report `join none` on the CRD that actually failed apply.

Not FIX: (1)+(2) are identity bugs, not crashes of an otherwise complete object. Duplicate counts, YAML blindness, and exit 0 on `disagree` are the ceiling written in CANDIDATE.md, still unbuilt.

---

## Mutation (what must change)

Keep the object: one query that names the identity field whose optionality disagrees with list-map (or patch-merge) identity.

Do not keep a regex that only replays the owned fixtures.

1. **Json identity is the json name.** No Go-name fallback when a json tag exists. `json:"-"` is not a key. `json:",omitempty"` is field name + omitempty (`disagree`, not `agree`). Duplicate json names on one struct are a reported collision, not first-wins.
2. **Specify the optionality axes and the verdict.** Today: json `omitempty` or `+optional`. Declare what protobuf `opt`, `omitzero`, `+kubebuilder:validation:Optional`, and `+default` do. The specimen rule is: list-map key must be **required or have a default**. Either join that (Go markers *and* YAML `required`/`default` / `x-kubernetes-list-map-keys`) or stop claiming the apply error.
3. **Refuse silent miss.** Unknown marker spellings, BOM, YAML, garbage, and `join none` on a file that contains `x-kubernetes-list-map-keys` or `+listMapKey` in a non-matching form must be rc≠0 or an explicit `unparsed` row. `agree` is a positive claim; it cannot be the default for a broken parse.
4. **`--check` exit 1 on `disagree` (and on `missing` unless opted out).** `disagree_n` counts distinct identity fields, not marker-line repeats. Accept multiple files / stdin concat as one package (already works as a blob; `a.go b.go` must not argparse-fail).
5. **Tests the fixtures cannot see:** `json:",omitempty"`, Go-name vs json-name mismatch, `json:"-"`, duplicate json names, duplicate `type` names, duplicate `+listMapKey`, YAML CRD keys, `+default`, BOM, spaces around `=`, embed/`json:",inline"`, untagged list field.

If the mutation cannot do (1)+(2)+(3), the object is still `grep` plus a HostAlias/Name table, and a later destroyer should KILL.

---

MUTATE
