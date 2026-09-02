# MUTATE tagjoin (third cut, TRANSFER YAML `|-` + DESTROYER_tagjoin_2 leftovers)

CLI sha256 before this cut: `94bb2f42350c40bf89f50ed63e72fe57d5b5e6017f9031ad08b4180f73f146b8` (second mutate, 32649 bytes)
CLI sha256 after:            `89a5144de349c3e1207b8939bc2312e4f22c4775820081a68488cd16e2e6ea09` (41876 bytes)
Original harvest (DESTROYER_tagjoin.md): `20b2ae10862f8f815f3284590ec3aac2455794de68de6726a1f565d634edc8b5`

Date: 2026-09-02 16:05 JST. Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin` (branch `specimen-hdd/candidate-tagjoin-tagjoin`, commit `fba93c8`). Not merged to `main`. No kubectl. No controller-gen. No OpenAPI emitter.

Keep the object: one query that names the identity field whose optionality disagrees with list-map identity. Owned 052 is still `disagree LocalObjectReference.Name` / `HostAlias.IP`.

Job: job-0405 worker=mutate-tagjoin-3. `TRANSFER_tagjoin_crd.md` was **MISS (unparsed)** on real CRDs because `description: |-` broke the indent-subset walker. `DESTROYER_tagjoin_2.md` KEEP leftovers: case-fold, `FILE.go FILE.yaml` concat drop, `versions:` sequence maps.

Later destroyer should **not** KILL the YAML path for this miss: real CRDs now name real keys (`conditions.type`, `claims.name`, ServiceMonitor `bindings.{group,resource,name,namespace}`), not `unparsed`. Kill only if a later pass restores `unparsed` on those CRDs, Go-name case-fold (`listMapKey=IP` vs `json:"ip"` as `disagree HostAlias.IP`), or `disagree_n 2` on documented `052-types.go crd-list-map.yaml`.

## What changed (this cut)

1. **YAML walker survives `|-` / wrapped scalars.** After a nonempty scalar, more-indented lines are consumed; they no longer `break` the parent map. `x-kubernetes-list-map-keys` after `description: |-` stays in the tree. Owned fragment `crd-list-map.yaml` still disagrees `imagePullSecrets.name` / `hostAliases.ip`.
2. **`versions:` sequence maps keep children.** `- name: v1` plus nested `schema:` is one object (`absorb_item_tail`). A versions-list CRD joins `hostAliases.ip`, not `unparsed`.
3. **JSON OpenAPI objects join.** `json.loads` when the text starts with `{` / `[`. Local `#/` `$ref` / `allOf` is followed for item `required` / `properties`. Unresolved `$ref` is `unparsed`, not a false `disagree`. Item-level `required` / `default` only (array-schema `required: [ip]` is still `disagree`).
4. **`FILE.go FILE.yaml` parses each path, then merges joins.** Documented order reports the two Go disagrees **and** the two YAML disagrees (`disagree_n 4`). Order no longer drops the CRD keys. Scan fallback still recovers list-map maps after a Go prefix in one blob.
5. **Json identity is the json name, case-sensitive.** Dropped `wn.lower() == key.lower()`. `listMapKey=IP` vs `json:"ip"` is `missing`, not `disagree HostAlias.IP`. Untagged `Name` vs `listMapKey=name` is `missing`. Empty json name is still the Go field name (`json:",omitempty"` + `listMapKey=Name` is `disagree`). `json:"inner,inline"` does not flatten. `+kubebuilder:default:foo` (colon) satisfies identity. Hyphenated YAML keys (`mount-path`) join.

Owned 052 is unchanged: `LocalObjectReference.Name` and `HostAlias.IP` are `disagree`. `--check` rc=1. Real v1.30.0 `types.go` still names those two plus `PodIP.IP` / `ObjectReference.Name`.

## Transfer CRDs (host-executed, not unparsed)

Scratch: `destroyers/_tagjoin_transfer_scratch/`. Same files as `TRANSFER_tagjoin_crd.md`.

| file | result | keys |
| --- | --- | --- |
| `kubernetes.crossplane.io_objects.yaml` | **TRANSFER** agree_n 1, unparsed_n 0, rc=0 | `conditions.type` required |
| `px.dev_viziers.yaml` | **TRANSFER** agree_n 1 | `claims.name` required |
| `monitoring.coreos.com_servicemonitors.yaml` | **TRANSFER** agree_n 5 | `bindings.{group,resource,name,namespace}`, `conditions.type` |
| `gateway.networking.k8s.io_httproutes.yaml` | **TRANSFER** agree_n 5 | `headers.name`, `add.name`, `set.name`, `queryParams.name`, `conditions.type` |
| `cert-manager.io_certificates.yaml` | **TRANSFER** agree_n 1 | `conditions.type` |
| `apis__apps__v1_openapi.json` | **TRANSFER** disagree_n 2, agree_n 16, unparsed_n 0 | **`hostAliases.ip` / `imagePullSecrets.name` disagree** (same specimen-052 keys); `conditions.type` agree via `$ref` |
| `k8s-core-v1-types.go` | **TRANSFER** disagree_n 4 | `LocalObjectReference.Name`, `HostAlias.IP`, `PodIP.IP`, `ObjectReference.Name` |

Crossplane / pixie / ServiceMonitor are no longer `unparsed	x-kubernetes-list-map-keys`.

## Tests / demo

`python3 tests/test_tagjoin.py` twice: 52 OK.

`./demo.sh` twice: byte-identical (`demo-1.log` / `demo-2.log`). `--check` on the owned fixture prints the two disagrees and `rc=1`; demo overall still exits 0.

New fixtures this cut: `crd-block-scalar.yaml`, `crd-versions.yaml`, `crd-list-map.json`, `crd-ref.yaml`, `crd-array-required.yaml`, `crd-hyphen-key.yaml`. `empty-json-name.go` key is `Name` (the wire name).

## Remaining failures (not faked)

- Still a field-line regex for Go and an indent YAML subset: no anchors, aliases, or tag types. Not a CRD generator.
- Go tags and YAML keys remain **separate rows**, not one merged HostAlias.IP ↔ hostAliases.ip object.
- Duplicate list-map nodes with the same `(list_name, key)` collapse (HTTPRoute 22 hits → 5 unique rows).
- protobuf `opt` is still not a verdict. `$ref` follow is local `#/` only.
- Tabs inside a json tag still split TSV columns.
- Exit 0 without `--check` still includes `disagree` (Unix filter via `--check` exists).

If a later pass restores `unparsed` on Crossplane/pixie/ServiceMonitor, Go-name case-fold, or silent YAML drop on `FILE.go FILE.yaml`, KILL that regression. Do not KILL this object as THIN_WRAPPER while the join still names which identity key is optional.

---

# MUTATE tagjoin (second cut, DESTROYER leftovers)

CLI sha256 before this cut: `366afb9c5c6a6c561afe1bfa49b693dd9ce06a6aae933ce5d59e13596f61071e` (first mutate)
CLI sha256 after:            `94bb2f42350c40bf89f50ed63e72fe57d5b5e6017f9031ad08b4180f73f146b8` (32649 bytes)
Original harvest (DESTROYER_tagjoin.md): `20b2ae10862f8f815f3284590ec3aac2455794de68de6726a1f565d634edc8b5`

Date: 2026-09-02. Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin` (branch `specimen-hdd/candidate-tagjoin-tagjoin`, commit `4835bb4`). Not merged to `main`. Binary name still `tagjoin`. No controller-gen.

Keep the object: one query that names the identity field whose optionality disagrees with list-map (or patch-merge) identity. Do not keep a regex that only replays the owned fixtures.

Later destroyer should **not** KILL as THIN_WRAPPER. (1)+(2)+(3) landed.

## What changed (this cut)

First mutate already had json identity, YAML join, `--check`, `unparsed`, `+default`. Leftovers from DESTROYER_tagjoin mutation 1–5 that this cut closes:

1. **Json identity is the json name** (still). No Go-name fallback when a json tag renamed the field (`listMapKey=IP` vs `json:"address"` is `missing`, not `disagree HostAlias.IP`). `json:"-"` is not a key. `json:",omitempty"` is Go field name + omitempty (`disagree`). Duplicate json names stay `collision`. **Duplicate `type` names are `collision`**, not last-wins (`dup-type.go` → `collision HostAlias.ip`, `--check` rc=1).
2. **Optionality axes (declared, used):** json `omitempty` / `omitzero` → optional; `+optional` / `+kubebuilder:validation:Optional` → optional; protobuf `opt` printed, **not** a verdict; `+default` / `+kubebuilder:default` / YAML `default` / YAML `required` satisfy identity (`agree`). Specimen rule: list-map key must be required or have a default.
3. **Refuse silent miss.** `+listMapKey = name` (spaces) joins. UTF-8 BOM is stripped, not `join none`. Same-line `// +listMapKey` attaches. Untagged slice fields join. `json:",inline"` / anonymous embeds flatten (`HostAlias` embedding `Base` names `HostAlias.IP`, not `missing`). `/* +listMapKey */` and identity-shaped text with no join are `unparsed` rc=2, not `agree` / `join none`.
4. **`--check` exit 1** on `disagree` / `missing` / `collision`. `--allow-missing` opts missing out. `disagree_n` is distinct identity rows (duplicate `+listMapKey` on one list counts once). `a.go b.go` is one package.
5. **Tests the fixtures could not see:** `json:",omitempty"`, Go-name vs json-name, `json:"-"`, duplicate json names, duplicate `type` names, duplicate `+listMapKey`, YAML CRD keys, `+default`, BOM, spaces around `=`, embed/`json:",inline"`, untagged list field, plus omitzero vs protobuf `opt` and block-comment `unparsed`.

Owned 052 is unchanged: `LocalObjectReference.Name` and `HostAlias.IP` are `disagree`. Required `json:"name"` is still `agree Item.Name`.

## Tests / demo

`python3 tests/test_tagjoin.py` twice: 35 OK.

`./demo.sh` twice: byte-identical (`demo-1.log` / `demo-2.log`). `--check` on the owned fixture prints the two disagrees and `rc=1`; demo overall still exits 0.

New fixtures this cut: `spaces-eq.go`, `embed-inline.go`, `untagged-list.go`, `dup-type.go`, `bom.go`.

## Remaining failures (not faked)

- Still a field-line regex, not Go: generics, type aliases, `[]struct{...}`, `*[]T` / arrays / maps, nested anonymous structs without a `type` name. Real `k8s.io/api` files still need a real parser.
- `+listMapKey` on the type (not the field) and `+patchMergeKey` without `+listMapKey` are not joins. The latter is `join none` rc=0 (no `+listMapKey` / `x-kubernetes-list-map-keys` hint).
- Go tags and YAML keys remain **separate rows**, not one merged HostAlias.IP ↔ hostAliases.ip object.
- YAML walker is an indent subset: no anchors, aliases, or multiline scalars. A CRD it cannot walk, if it still contains `x-kubernetes-list-map-keys`, is `unparsed` rather than a fake `agree`.
- protobuf `opt` is still not a verdict (declared). `+default` is a marker proxy, not proof the generated OpenAPI emitted `default`.
- Tabs inside a json tag still split TSV columns. `other_omitempty` is still one fat line.
- Exit 0 without `--check` still includes `disagree` (Unix filter via `--check` exists).

If a later pass restores Go-name fallback, `agree` on `json:",omitempty"`, or `join none` rc=0 on identity-shaped text, KILL that regression. Do not KILL this object as THIN_WRAPPER while the join still names which identity key is optional.
