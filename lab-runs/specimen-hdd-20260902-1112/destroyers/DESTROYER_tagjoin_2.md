# DESTROYER tagjoin 2

Date: 2026-09-02 15:40 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0343 worker=destroyer-tagjoin-2

Target (lineage archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin`

Worktree (byte-identical): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin/tagjoin/tagjoin`

sha256 `94bb2f42350c40bf89f50ed63e72fe57d5b5e6017f9031ad08b4180f73f146b8` (32649 bytes). HEAD `4835bb4` (`Mutate tagjoin leftovers: dup types, inline embeds, silent-miss.`). Parent `main` has no `tagjoin`. Not merged. No controller-gen. Host Python 3.14.5.

`python3 tests/test_tagjoin.py`: 35/35 OK. `./demo.sh` twice this pass: byte-identical, `--check` owned fixture `rc=1`, demo overall `rc=0`.

Origin claim: name the field whose optionality tags disagree with `+listMapKey` identity. Specimen-052. Kind: USEFUL_COMPOSITION.

First destroyer (`DESTROYER_tagjoin.md`) → **MUTATE**. Required (1) json identity is the json name, (2) optionality axes / specimen rule required-or-default, (3) refuse silent miss. Kill if a later pass could not do those, or restored Go-name fallback / `agree` on `json:",omitempty"` / `join none` rc=0 on identity-shaped text.

MUTATE.md claimed (1)+(2)+(3) landed. Host-executed, not trusted. **Those Honor-KILL conditions did not fire.** This is not THIN_WRAPPER of a HostAlias grep table. Decision: **MUTATE** (leftovers of json-name exactness and the advertised YAML package), not KILL, not FIX.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/fixtures
S052=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052
```

No merge onto `main`. No controller-gen, no cluster, no OpenAPI emitter.

---

## Honor-KILL check (host-executed)

| condition | observed | kill? |
| --- | --- | --- |
| THIN_WRAPPER of grep HostAlias table | Unseen `containerPort` transfers; required `json:"name"` is `agree Item.Name`; YAML fragment names `hostAliases.ip`; apply-error text names both keys. Grep still hits list tags + `Hostnames` without the join. | no |
| Go-name fallback restored | `listMapKey=ip` vs `json:"address,omitempty"` on field `IP` → `missing HostAlias.ip`, not `disagree HostAlias.IP`. `listMapKey=IP` vs `json:"address"` → `missing`. `json:"-"` → `missing`, not `agree`. | no |
| `agree` on `json:",omitempty"` | `disagree Item.Name`, json column `,omitempty`, optional `omitempty`, `disagree_n 1`. `// +listMapKey=omitempty` no longer invents a json name `omitempty` (`missing Item.omitempty`). | no |
| `join none` rc=0 on identity-shaped text | `x-kubernetes-list-map-keys` prose → `unparsed` rc=2. `+listMapKey` prose → `unparsed` rc=2. `/* +listMapKey */` → `unparsed` rc=2. Empty `package p` still `join none` rc=0 (no hint). | no |

Owned 052 still names both identity keys:

```text
python3 "$CLI" "$FX/052-types.go"
python3 "$CLI" --check "$FX/052-types.go"; echo rc=$?
python3 "$CLI" "$S052/files/types_excerpt.go"
```

```text
disagree	LocalObjectReference.Name	...	json	name,omitempty	optional	+optional,omitempty	...
disagree	HostAlias.IP	...	json	ip,omitempty	optional	omitempty	...
other_omitempty	HostAlias.Hostnames
disagree_n	2
--check rc=1
```

`--check` on `agree-name.go` is rc=0. Duplicate `+listMapKey=name` twice: `disagree_n 1`. Duplicate `type HostAlias`: `collision` / `--check` rc=1. BOM fixture starts `\xef\xbb\xbf` and is `agree Item.Name`. `+listMapKey = name` (spaces) joins. Same-line `// +listMapKey=name` joins. `+default=""` on omitempty is `agree`. protobuf `opt` with required json is `agree` (printed, not a verdict). `omitzero` is `disagree`. FIFO with a writer works. 400 list+elem pairs: 400 `disagree` rows, 0.036s. Invalid UTF-8: rc=2, `tagjoin: 'utf-8' codec can't decode...`, no traceback.

That is the mutation that landed. Attacks below are the leftover identity, not a re-run of the closed holes.

---

## What still works

The owned wrapped fixture, the loose excerpt, unseen Ports, YAML *flattened fragments*, apply-error text, json-empty-name, wrong-wire, json dash, collisions, `--check`, BOM / spaces / inline embed / untagged list / split `a.go`+`b.go` of two Go files.

`grep -nE 'omitempty|listMapKey|\+optional'` on `052-types.go` still hits list `+optional`, list `listMapKey`, `Hostnames`, and the identity keys without saying which key is optional. tagjoin still names `LocalObjectReference.Name` and `HostAlias.IP`.

---

## Implementation

### 1. Json identity is still case-folded

`find_key_hits` matches exact wire name, else `wn.lower() == key.lower()`. First destroyer called `listMapKey=IP` vs `json:"ip"` a Go-name case-fold. The mutate removed Go-name match when the json tag *renamed* the field (`address`). It kept case-fold of the *wire* name. For the IP/ip pair that is the same join.

Host `inspect()`:

```text
listMapKey=IP  vs json:"ip,omitempty"  → disagree HostAlias.IP   json=ip,omitempty
listMapKey=ip  vs json:"IP,omitempty"  → disagree HostAlias.IP   json=IP,omitempty
listMapKey=IP  vs json:"address" + sibling json:"ip"          → disagree HostAlias.Addr
listMapKey=name vs untagged `Name string`                     → agree Item.Name  json=Name
```

encoding/json and OpenAPI properties are case-sensitive. `+listMapKey=ip` is the json name `ip`. A field whose wire name is `IP` is a different property. An untagged `Name` serializes as `Name`, not `name`. tagjoin reports a disagreement (or an agree) on a property the generated OpenAPI would not use as the map key.

`json:"-"` does not take this path (wire name is `None`). `json:"address"` does not fold to `ip`. Those tests are green and do not see this hole.

### 2. Documented `tagjoin FILE.go FILE.yaml` swallows the YAML

README / CANDIDATE.md: `tagjoin FILE.go FILE.yaml`. Multiple files are concatenated as one blob, then *one* YAML walk on the whole text.

Go-first (the documented order): `load_yaml_subset` hits `package v1` (no `:`), returns `{}`. `inspect_yaml_schema` sees `x-kubernetes-list-map-keys` in the text, walks an empty tree, returns `[]`. Go already produced joins, so `unparsed` stays empty.

```text
python3 "$CLI" "$FX/052-types.go" "$FX/crd-list-map.yaml"
# disagree LocalObjectReference.Name, HostAlias.IP
# disagree_n 2     ← YAML hostAliases.ip / imagePullSecrets.name absent
# rc=0
```

YAML-first is the opposite: four `disagree` rows, `disagree_n 4`. Same two files, order-dependent package. That is not “one package”. It is also not `unparsed` — a silent drop of the CRD keys while claiming a successful Go join.

`inspect_apply_error` still fires on apply-error text even after Go, because it is a regex over the blob. YAML is the walker that dies on a Go prefix.

### 3. A real CRD is `unparsed`, not a join

Flattened `fixtures/crd-list-map.yaml` and the OBSERVED.md fragment join (`imagePullSecrets.name` / `hostAliases.ip`, optional `not-required`). A versions-list CRD does not:

```text
spec:
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        properties:
          hostAliases:
            x-kubernetes-list-map-keys: [ip]
            ...
```

`load_yaml_subset` parses `- name: v1` as `{name: v1}` and **drops** the nested `schema:` children (`indent > seq_indent` breaks the sequence). Observed tree:

```text
{'apiVersion': '...', 'kind': 'CustomResourceDefinition', 'spec': {'versions': [{'name': 'v1'}]}}
```

`x-kubernetes-list-map-keys` is in the text → `unparsed` rc=2, not a fake `agree`. Honest miss. Also not the advertised CRD join. JSON CRDs (`"x-kubernetes-list-map-keys": ["ip"]`) are the same `unparsed` rc=2. YAML `$ref` to a definition that `required: [ip]` is **false `disagree`** (walker never follows `$ref`). Array-schema `required: [ip]` (wrong level) is **false `agree`** (`_yaml_key_state` unions `node.required` with `items.required`).

Hyphenated list-map keys (`mount-path`) fail `YAML_KEY_RE` (`\w` only), become `unparsed`. k8s keys are usually camelCase; still a silent drop of a key that was in the file.

### 4. Other leftover identity, not crashes

| input | observed |
| --- | --- |
| `Inner Base \`json:"inner,inline"\`` | flattens; `disagree HostAlias.IP`. encoding/json would nest under `inner`. `json:",inline"` (empty name) is the k8s embed the mutate meant. |
| `// +kubebuilder:default:foo` (colon) | still `disagree`. `// +kubebuilder:default=foo` is `agree`. |
| `+default` on the **list** field | does not satisfy the key (`disagree`, `has_default False`). Correct axis, easy to misread. |
| `+patchMergeKey=ip` only | `join none` rc=0 (`identity_hints` does not treat patch-merge as a hint). Declared remaining. |
| `*[]HostAlias` / type alias / `[]struct{...}` / generics | `missing` or `unparsed`. Declared field-line regex ceiling. |
| Go tags + YAML keys | even when both parse (YAML-first), separate rows, not one HostAlias.IP ↔ hostAliases.ip object. Declared. |
| `--check` without flag | `disagree` is still rc=0. Unix filter exists. |

Invalid UTF-8 rc=2 is clean. Directory / missing file rc=1, `tagjoin:` prefix. Tabs inside a json name make the key `missing` (wire name is not `name`); the TSV bomb the first destroyer saw only happens if that name *is* the key.

---

## Primitive

Reality-stripped operation: line-regex Go tags; collect `+listMapKey` on slice fields; look up that string as a json wire name **with case-fold**; `disagree` iff omitempty/omitzero/`+optional` and no `+default`. Plus an indent YAML subset on flattened `x-kubernetes-list-map-keys` fragments, and a regex over apply-error `properties[list].items.properties[key]`.

Nearest ordinary workflow: `grep omitempty` and `grep listMapKey` in one Go file, then a hand look at the element type. After this mutate that join is still the useful delta, and it is no longer the broken `json:",omitempty"` / Go-name-on-`address` / `join none` on identity text object the first destroyer killed.

Lost if the **CLI** vanishes: naming which identity key is optional, including unseen `containerPort`, `json:",omitempty"` as empty name + omitempty, `json:"-"` as not a key, collision vs last-wins, `--check` rc=1, apply-error rows.

Lost if the **question** is a real CRD document or the documented `FILE.go FILE.yaml` invocation: the YAML half is either `unparsed` (versions list / JSON) or silently absent (Go-first concat). Grep of `x-kubernetes-list-map-keys` on that CRD still shows `ip` / `name`. tagjoin does not.

That is why this is not KILL: (1)+(2)+(3) landed on the Go-tag object and on flattened YAML / apply-error text. Owned 052 is still the join grep will not emit.

Not FIX: case-fold and Go-first YAML drop are identity bugs of the advertised package, not crashes of an otherwise complete object.

---

## Mutation (what must change)

Keep the object: one query that names the identity field whose optionality disagrees with list-map (or patch-merge) identity.

Do not keep a case-fold that reimplements Go-name matching for `IP`/`ip`, or a “one package” concat that drops YAML when the first file is Go.

1. **Json identity is the json name, case-sensitive.** Drop `wn.lower() == key.lower()`. `listMapKey=IP` vs `json:"ip"` is `missing` (or an explicit `case-mismatch` row), not `disagree HostAlias.IP`. Untagged `Name` vs `listMapKey=name` is `missing` (wire name `Name`). `json:"IP"` vs `listMapKey=ip` is `missing`. Keep: empty json name = Go field name; `json:"-"` is not a key; `json:"address"` is not `ip`; duplicate json names are `collision`.

2. **`FILE.go FILE.yaml` must actually join both.** Parse each path (or each fragment) separately and merge joins. Documented order `052-types.go` + `crd-list-map.yaml` must report the two Go disagrees **and** the two YAML disagrees (or one merged HostAlias.IP ↔ hostAliases.ip object), not `disagree_n 2` with the CRD keys gone. A blob that contains `x-kubernetes-list-map-keys` whose walker returned no keys is `unparsed`, even if Go already joined.

3. **CRD `versions:` sequence maps keep their children.** `- name: v1` plus nested `schema:` is one object. A CRD that contains `x-kubernetes-list-map-keys` must join those keys or stay `unparsed` *and* stop advertising `tagjoin FILE.go FILE.yaml` as the CRD path. Item-level `required` / `default` only (`items.required`, `items.properties[k].default`). `$ref` is `unparsed` or followed, not false `disagree`. Do not treat array-schema `required` as the map-key required set.

4. **`json:"name,inline"` is not an embed.** Only empty-name `json:",inline"` / anonymous embeds flatten. `+kubebuilder:default:foo` and `+kubebuilder:default=foo` are the same axis, or declare the colon form unparsed.

Tests the current 35 cannot see: `listMapKey=IP` vs `json:"ip"`; untagged `Name` vs `listMapKey=name`; `python3 tagjoin 052-types.go crd-list-map.yaml` (documented order); a `versions: - name: v1` CRD; JSON CRD; YAML `$ref`; array-level `required: [ip]`.

If the mutation cannot do (1)+(2), the object is still the Go-tag fixture replay plus a YAML-only fragment parser that the documented CLI invocation does not run, and a later destroyer should KILL.

Do not merge onto `main`. Do not run controller-gen.

---

MUTATE
