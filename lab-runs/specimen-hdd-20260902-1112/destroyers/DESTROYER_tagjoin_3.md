# DESTROYER tagjoin 3

Date: 2026-09-02 16:20 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0426 worker=destroyer-tagjoin-3

Target (lineage archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin`

Worktree (byte-identical): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin/tagjoin/tagjoin`

sha256 `89a5144de349c3e1207b8939bc2312e4f22c4775820081a68488cd16e2e6ea09` (41876 bytes). Matches `MUTATE.md` after mutate-3. HEAD `fba93c8` (`Mutate tagjoin YAML walker: survive |-, versions sequences, JSON.`). Archive `HEAD.txt` is `fba93c8b8dab46366c74e853ba7d8581c35777fa`. Parent `main` `432f954`; `git ls-tree -r HEAD` has **no** `tagjoin`. Not merged. No kubectl. No controller-gen. No cluster. Host Python 3.14.5.

`python3 tests/test_tagjoin.py`: **52/52 OK** twice (1.197s / 1.199s, rc=0). `./demo.sh` twice this pass: byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 8167 bytes). `--check` owned fixture `rc=1`; demo overall `rc=0`.

Origin claim: name the identity field whose optionality disagrees with list-map identity. Specimen-052. Kind: USEFUL_COMPOSITION.

Prior: `DESTROYER_tagjoin.md` **MUTATE**. `DESTROYER_tagjoin_2.md` first **KEEP** then **MUTATE** leftovers (case-fold, `FILE.go FILE.yaml` concat drop, `versions:` sequence maps). `TRANSFER_tagjoin_crd.md` **MISS (unparsed)** on real CRDs because `description: |-` broke the indent walker. Mutate-3 claimed those closed. First KEEP/MUTATE is not protection. Honor KILL if this cut restores `unparsed` on Crossplane/pixie/ServiceMonitor, Go-name case-fold (`listMapKey=IP` vs `json:"ip"` as `disagree HostAlias.IP`), silent `disagree_n 2` on documented `052-types.go crd-list-map.yaml`, or THIN_WRAPPER of a grep HostAlias table (no join).

MUTATE.md claimed (YAML `|-` walker + versions sequence maps + JSON OpenAPI + FILE.go FILE.yaml merge + json-name case-sensitive). Host-executed, not trusted. **Those Honor-KILL conditions did not fire.** Remaining leftovers (anchors, separate Go/YAML rows, duplicate collapse, protobuf `opt`, tabs, rc=0 without `--check`) are the declared indent-subset ceiling, not a regression. Decision: **KEEP**. Not FIX. Not a required MUTATE of the object. Not KILL. No fossil.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/fixtures
S052=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052
TR=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_tagjoin_transfer_scratch
SCRATCH=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_tagjoin3_scratch
```

No merge onto `main`. No controller-gen. No cluster. Do not grow a full YAML parser / CRD generator to escape a KILL that does not apply.

---

## Honor-KILL check (host-executed)

| condition | observed | kill? |
| --- | --- | --- |
| TRANSFER CRDs restore `unparsed` on `x-kubernetes-list-map-keys` | Crossplane `agree conditions.type` unparsed_n 0 rc=0. Pixie `agree claims.name`. ServiceMonitor `agree bindings.{group,resource,name,namespace}` + `conditions.type`. HTTPRoute `agree` 5 unique keys (file has 22 hits). cert-manager `agree conditions.type` (4 hits collapse to 1). OpenAPI JSON `disagree hostAliases.ip` / `imagePullSecrets.name`, `agree_n 16`, unparsed_n 0. | **no** |
| Go-name case-fold restored (`listMapKey=IP` vs `json:"ip"` as `disagree HostAlias.IP`) | `missing HostAlias.IP`, not `disagree`. `listMapKey=ip` vs `json:"IP"` → `missing HostAlias.ip`. Untagged `Name` vs `listMapKey=name` → `missing Item.name`. `json:"address"` on field `IP` → `missing`. Sibling `json:"ip"` with key `IP` → `missing`. | **no** |
| `disagree_n 2` silently dropped on documented `052-types.go` + `crd-list-map.yaml` | Go-then-YAML **and** YAML-then-Go: `disagree_n 4` (`LocalObjectReference.Name`, `HostAlias.IP`, `imagePullSecrets.name`, `hostAliases.ip`). Concat blob on stdin also `disagree_n 4`. `--check` on the pair rc=1. | **no** |
| THIN_WRAPPER of grep HostAlias table (no join) | `grep -nE 'omitempty\|listMapKey\|\+optional'` hits list `+optional`, list `listMapKey`, `Hostnames`, and the identity keys **without** saying which key is optional. tagjoin names `LocalObjectReference.Name` and `HostAlias.IP` as `disagree`; list omitempty is not the join (`agree-name.go` → `agree Item.Name`); unseen `containerPort` transfers (`disagree ContainerPort.ContainerPort`). | **no** |

MUTATE.md said do not KILL as THIN_WRAPPER while the join still names which identity key is optional. It still does, including on the TRANSFER CRDs that were `unparsed` before this cut.

Owned 052 still names both identity keys:

```text
python3 "$CLI" "$FX/052-types.go"
python3 "$CLI" --check "$FX/052-types.go"; echo rc=$?
python3 "$CLI" "$S052/files/types_excerpt.go"
python3 "$CLI" "$FX/052-types.go" "$FX/crd-list-map.yaml"
```

```text
disagree	LocalObjectReference.Name	...	json	name,omitempty	optional	+optional,omitempty	...
disagree	HostAlias.IP	...	json	ip,omitempty	optional	omitempty	...
other_omitempty	HostAlias.Hostnames
disagree_n	2
--check rc=1

# documented FILE.go FILE.yaml
disagree	LocalObjectReference.Name
disagree	HostAlias.IP
disagree	imagePullSecrets.name
disagree	hostAliases.ip
disagree_n	4
--check rc=1
```

---

## What mutate-3 claimed, host-executed

1. **YAML walker survives `|-` / wrapped scalars.** Owned `crd-block-scalar.yaml`: `agree conditions.type` / `claims.name`, unparsed_n 0. Synthetic `versions:` + `description: |-` then `x-kubernetes-list-map-keys: [type]` → `agree conditions.type`. Folded `>` and plain `|` (no dash) also keep the sibling keys.
2. **`versions:` sequence maps keep children.** `crd-versions.yaml`: `disagree hostAliases.ip` / `imagePullSecrets.name`, not `unparsed`.
3. **JSON OpenAPI objects join.** `crd-list-map.json` and v1.30.0 `apis__apps__v1_openapi.json` (827632 bytes, 24 list-map hits): `disagree hostAliases.ip` / `imagePullSecrets.name`, `agree_n 16`, unparsed_n 0. Local `$ref` followed (conditions.type agree). Unresolved / external `$ref` is `unparsed` rc=2, not a false `disagree`. Array-schema `required: [ip]` is still `disagree` (item-level only).
4. **`FILE.go FILE.yaml` parses each path, then merges.** Documented order reports four disagrees. Order no longer drops the CRD keys. Scan fallback recovers list-map maps after a Go prefix in one blob (`cat 052-types.go crd-list-map.yaml | tagjoin -` → `disagree_n 4`).
5. **Json identity is the json name, case-sensitive.** Dropped `wn.lower() == key.lower()`. Empty json name is still the Go field name (`json:",omitempty"` + `listMapKey=Name` is `disagree`; + `listMapKey=name` is `missing`). `json:"inner,inline"` does not flatten. `+kubebuilder:default:foo` (colon) satisfies identity. Hyphenated YAML keys (`mount-path`) join.

TRANSFER CRDs (same files as `TRANSFER_tagjoin_crd.md`; scratch still mounted):

| file | result | keys |
| --- | --- | --- |
| `kubernetes.crossplane.io_objects.yaml` | TRANSFER agree_n 1, unparsed_n 0, rc=0; `--check` rc=0 | `conditions.type` required |
| `px.dev_viziers.yaml` | TRANSFER agree_n 1 | `claims.name` required |
| `monitoring.coreos.com_servicemonitors.yaml` | TRANSFER agree_n 5 | `bindings.{group,resource,name,namespace}`, `conditions.type` |
| `gateway.networking.k8s.io_httproutes.yaml` | TRANSFER agree_n 5 (22 file hits) | `headers.name`, `add.name`, `set.name`, `queryParams.name`, `conditions.type` |
| `cert-manager.io_certificates.yaml` | TRANSFER agree_n 1 (4 file hits) | `conditions.type` |
| `apis__apps__v1_openapi.json` | TRANSFER disagree_n 2, agree_n 16 | **`hostAliases.ip` / `imagePullSecrets.name` disagree** (specimen-052 keys) |
| `k8s-core-v1-types.go` | TRANSFER disagree_n 4, agree_n 25, missing_n 1; `--check` rc=1 | `LocalObjectReference.Name`, `HostAlias.IP`, `PodIP.IP`, `ObjectReference.Name`; `Condition.type` missing (metav1 lives in another file) |
| `argoproj.io_applications.yaml` | `join none` rc=0 | zero list-map hits; not this miss |

Crossplane / pixie / ServiceMonitor are no longer `unparsed	x-kubernetes-list-map-keys`.

---

## Remaining leftovers (attacked; declared ceiling; not Honor-KILL)

These are the list MUTATE.md left as “not faked”. Host-executed this pass. They do not restore the closed holes.

### 1. Anchors / aliases / tag types

Indent subset, not a YAML parser.

| input | observed |
| --- | --- |
| `x-kubernetes-list-map-keys: &keys` then `required: *keys` | `unparsed` rc=2 (honest miss, not false `agree`) |
| `<<: *lm` merge onto `hostAliases` | joins the **definition** (`agree listmap.ip`), not the merge target |
| `podIPs: *ha` alias of a whole list-map node | joins the original `hostAliases.ip` only |
| `x-kubernetes-list-map-keys: !!seq` | `unparsed` rc=2 |
| flow mapping `{x-kubernetes-list-map-keys: [ip], ...}` | `unparsed` rc=2 |

A CRD that still contains the hint string and yields no join stays `unparsed`, not `agree`. Real TRANSFER CRDs in the scratch dir do not need anchors.

### 2. Go vs YAML remain separate rows

`tagjoin 052-types.go crd-list-map.yaml` prints `HostAlias.IP` **and** `hostAliases.ip`, not one merged object. Declared. The documented invocation no longer *drops* the YAML half.

### 3. Duplicate list-map collapse

`(list_name, key)` is unique. HTTPRoute 22 hits → 5 unique required rows. cert-manager 4 hits → 1 `conditions.type`. Synthetic two `hostAliases` nodes, first optional then required: **first wins** (`disagree hostAliases.ip`; the required sibling is invisible). Real TRANSFER CRDs collapse identical required keys, not mixed optionality. Declared.

### 4. protobuf `opt` is not a verdict

`json:"name"` + `protobuf:"...,opt,..."` is `agree Item.Name`, protobuf column `opt`. Printed, ignored. Declared axis.

### 5. Tabs inside json tags

`json:"na\tme,omitempty"` vs `listMapKey=name` is `missing` (wire name is not `name`). `// +listMapKey=na<TAB>me` does not match `MARKER_RE` (`\S` stops at the tab) → `unparsed +listMapKey` rc=2. TSV columns still split if a joined json name contains a tab. Declared.

### 6. Exit 0 without `--check` still includes `disagree`

Owned 052 without the flag: `disagree_n 2` rc=0. With `--check`: same rows, rc=1. Unix filter exists. 400 list+elem pairs: 400 `disagree` rows, rc=0, no cap.

Other declared ceilings still hold: field-line regex (generics / type aliases / `*[]T`); `+patchMergeKey` without `+listMapKey` is `join none` rc=0 (no identity hint); `+listMapKey` prose / `/* +listMapKey */` is `unparsed` rc=2.

---

## Primitive

Reality-stripped operation: line-regex Go tags; collect `+listMapKey` on slice fields; look up that string as a **case-sensitive json wire name**; `disagree` iff omitempty/omitzero/`+optional` and no `+default`. Plus an indent YAML subset that keeps siblings after `|-` and `versions:` sequence children, JSON `json.loads` when the text starts with `{`/`[`, local `#/` `$ref` / `allOf`, and a regex over apply-error `properties[list].items.properties[key]`. Multiple paths are parsed separately, then joins merge.

Nearest ordinary workflow: `grep omitempty` and `grep listMapKey` in one Go file, then a hand look at the element type. After mutate-3 that join is still the useful delta, and it is no longer the `description: |-` / case-fold / Go-first YAML-drop object DESTROYER_2 and TRANSFER killed.

Lost if the **CLI** vanishes: naming which identity key is optional — owned `HostAlias.IP` / `LocalObjectReference.Name`, unseen `containerPort`, real CRD `conditions.type` / pixie `claims.name` / ServiceMonitor `bindings.*`, OpenAPI `hostAliases.ip` still `disagree`, `json:",omitempty"` as empty name + omitempty, `json:"-"` as not a key, `listMapKey=IP` vs `json:"ip"` as `missing`, `--check` rc=1, `FILE.go FILE.yaml` both halves.

Lost if the **question** is a full YAML document with anchors/aliases/flow maps, or one merged HostAlias.IP ↔ hostAliases.ip object: the indent subset `unparsed`s or names the definition, not the alias. Grep of `x-kubernetes-list-map-keys` still shows the keys. That is the declared ceiling, not the TRANSFER miss.

That is why this is **KEEP**, not KILL: Honor-KILL regressions did not fire; the join still names which identity key is optional on owned 052, on v1.30.0 types.go, and on the CRDs that were `unparsed` before this cut.

Not FIX: remaining leftovers are the indent-subset / TSV / `--check` ceiling written in MUTATE.md, still unbuilt, still honest (`unparsed` rather than false `agree` on aliases).

Not a required MUTATE: growing a YAML parser, a Go↔YAML object merge, or making protobuf `opt` a verdict would rebuild a CRD generator. Research boundary forbids that. Do not send that theater back to R1.

---

Do not merge onto `main`. Do not run controller-gen. Do not apply CRDs.

---

KEEP
