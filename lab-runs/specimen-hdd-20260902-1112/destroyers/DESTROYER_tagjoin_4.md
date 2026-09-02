# DESTROYER tagjoin 4

Date: 2026-09-02 19:35–19:44 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0591 worker=destroyer-tagjoin-4

Target (lineage archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin`

Worktree (byte-identical): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-tagjoin-tagjoin/tagjoin/tagjoin`

sha256 `89a5144de349c3e1207b8939bc2312e4f22c4775820081a68488cd16e2e6ea09` (41876 bytes). Matches `MUTATE.md` after mutate-3. HEAD `fba93c8` (`Mutate tagjoin YAML walker: survive |-, versions sequences, JSON.`). Archive `HEAD.txt` is `fba93c8b8dab46366c74e853ba7d8581c35777fa`. Parent `main` `432f954`; `git ls-tree -r HEAD` has **no** `tagjoin`. Not merged. No kubectl. No controller-gen. No cluster. Host Python 3.14.5. Worktree was not edited (`cmp` rc=0).

`python3 tests/test_tagjoin.py`: **52/52 OK** twice (1.505s / 1.392s, rc=0). `./demo.sh` twice this pass: byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 8167 bytes, sha256 `5d9bb4f74c02fd8e743e506b106979782dfbdd81bff8f5257bc8ef9e9c7e411c`). `--check` owned fixture `rc=1`; demo overall `rc=0`.

Origin claim: name the identity field whose optionality disagrees with list-map identity. Specimen-052. Kind: USEFUL_COMPOSITION.

Prior: `DESTROYER_tagjoin.md` **MUTATE**. `DESTROYER_tagjoin_2.md` **MUTATE**. `DESTROYER_tagjoin_3.md` **KEEP**. First KEEP is not protection. Honor KILL if TRANSFER CRDs restore `unparsed` on Crossplane/pixie/ServiceMonitor, Go-name case-fold (`listMapKey=IP` vs `json:"ip"` as `disagree HostAlias.IP`), silent `disagree_n 2` on documented `052-types.go crd-list-map.yaml`, or THIN_WRAPPER of a grep HostAlias table (no join).

MUTATE.md remaining failures (anchors, separate Go/YAML rows, duplicate collapse, protobuf `opt`, tabs, rc=0 without `--check`) were re-attacked as leftover-identity, not trusted as ceiling. **Honor-KILL conditions did not fire.** Real TRANSFER CRDs still name identity keys (`conditions.type` / `claims.name` / `bindings.*`); owned 052 still names `LocalObjectReference.Name` / `HostAlias.IP`. Synthetic required-then-optional first-wins is the declared `(list_name, key)` uniqueness, not a lie on any TRANSFER file (mixed optionality count 0). Remaining cuts that would parse anchors/aliases/flow maps need a full YAML parser. Worst-wins / version-diff across mixed CRD versions would grow a CRD generator. Decision: **KEEP**. Not FIX. Not a required MUTATE of the object. Not KILL. No fossil.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/tagjoin
FX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-tagjoin/fixtures
S052=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052
TR=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_tagjoin_transfer_scratch
SCRATCH=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_tagjoin4_scratch
```

No merge onto `main`. No controller-gen. No cluster. Do not grow a full YAML parser / CRD generator to escape a KILL that does not apply.

Attack log: `destroyers/_tagjoin4_scratch/attack.log` (host-executed `attack.py`).

---

## Honor-KILL check (host-executed)

| condition | observed | kill? |
| --- | --- | --- |
| TRANSFER CRDs restore `unparsed` on `x-kubernetes-list-map-keys` | Crossplane `agree conditions.type` unparsed_n 0 rc=0; `--check` rc=0. Pixie `agree claims.name`; `--check` rc=0. ServiceMonitor `agree bindings.{group,resource,name,namespace}` + `conditions.type`; `--check` rc=0. HTTPRoute `agree` 5 unique keys (file has 22 hits). cert-manager `agree conditions.type` (4 hits collapse to 1). OpenAPI JSON `disagree hostAliases.ip` / `imagePullSecrets.name`, `agree_n 16`, unparsed_n 0; `--check` rc=1. | **no** |
| Go-name case-fold restored (`listMapKey=IP` vs `json:"ip"` as `disagree HostAlias.IP`) | `missing HostAlias.IP`, not `disagree`. `listMapKey=ip` vs `json:"IP"` → `missing HostAlias.ip`. Untagged `Name` vs `listMapKey=name` → `missing Item.name`. `json:"address"` on field `IP` → `missing`. Sibling `json:"ip"` with key `IP` → `missing`. | **no** |
| `disagree_n 2` silently dropped on documented `052-types.go` + `crd-list-map.yaml` | Go-then-YAML **and** YAML-then-Go: `disagree_n 4` (`LocalObjectReference.Name`, `HostAlias.IP`, `imagePullSecrets.name`, `hostAliases.ip`). Concat blob on stdin also `disagree_n 4`. `--check` on the pair rc=1. | **no** |
| THIN_WRAPPER of grep HostAlias table (no join) | `grep -nE 'omitempty\|listMapKey\|\+optional'` hits list `+optional`, list `listMapKey`, `Hostnames`, and the identity keys **without** saying which key is optional. tagjoin names `LocalObjectReference.Name` and `HostAlias.IP` as `disagree`; list omitempty is not the join (`agree-name.go` → `agree Item.Name`); unseen `containerPort` transfers (`disagree ContainerPort.ContainerPort`). | **no** |

MUTATE.md said do not KILL as THIN_WRAPPER while the join still names which identity key is optional. It still does, including on the TRANSFER CRDs that were `unparsed` before mutate-3.

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

## Leftover re-attack (anchors / duplicate collapse)

Job input: leftover YAML anchors / duplicate collapse after DESTROYER_tagjoin_3 KEEP. First KEEP is not protection. Host-executed; not a rubber stamp.

### Duplicate collapse — declared uniqueness, not a TRANSFER lie

`_joins_from_tree` keys `(list_name, key)` first-wins. Synthetic mixed optionality:

| input | CLI | walker honesty |
| --- | --- | --- |
| optional then required `hostAliases.ip` | `disagree` | `['disagree', 'agree']` |
| required then optional | `agree` (hides later disagree) | `['agree', 'disagree']` |
| `versions:` v1 required / v2 optional | `agree` | `['agree', 'disagree']` |
| JSON object a required / b optional | `agree` | `['agree', 'disagree']` |

The indent subset **already sees both nodes**. A worst-wins / `collision` on mixed verdicts would be a few lines, not a YAML parser.

That is still **not** a required MUTATE of this object:

- Real TRANSFER files: **mixed optionality count 0**. Crossplane `conditions.type` 2× agree. HTTPRoute `add.name` 8× agree, `set.name` 8× agree, `headers.name` 2×, `queryParams.name` 2×, `conditions.type` 2×. OpenAPI 18 unique keys, 6 duplicated, all same-verdict (including specimen keys `hostAliases.ip` / `imagePullSecrets.name` as disagree, not hidden). cert-manager 4 hits → 1 `conditions.type` agree.
- MUTATE.md already declared `(list_name, key)` collapse (HTTPRoute 22 → 5 unique required rows). DESTROYER_3 host-executed first-wins and left it as ceiling.
- Two CRD versions with mixed optionality is a version-diff. Growing that into collision/worst-wins is a CRD generator, which the research boundary forbids.
- The join still names which identity key is optional on owned 052, v1.30.0 types.go (`HostAlias.IP` / `LocalObjectReference.Name` / `PodIP.IP` / `ObjectReference.Name`), and every TRANSFER CRD that carries list-map keys.

Two keys on one node with mixed required (`[ip, hostname]`, only `ip` required) still prints **both** rows (`agree hostAliases.ip` + `disagree hostAliases.hostname`). Collapse is same-key uniqueness, not a dropped sibling key.

### Anchors / aliases / tag types — need a YAML parser

Indent subset, honest miss, not false `agree` on an alias target.

| input | observed |
| --- | --- |
| `x-kubernetes-list-map-keys: &keys` then `required: *keys` | `unparsed` rc=2 |
| `<<: *lm` merge onto `hostAliases` | joins the **definition** (`agree listmap.ip`), not the merge target |
| `podIPs: *ha` alias of a whole list-map node | joins the original `hostAliases.ip` only |
| `x-kubernetes-list-map-keys: !!seq` | `unparsed` rc=2 |
| flow mapping `{x-kubernetes-list-map-keys: [ip], ...}` | `unparsed` rc=2 |

A CRD that still contains the hint string and yields no join stays `unparsed`, not `agree`. Real TRANSFER CRDs in the scratch dir do not need anchors.

Quoted keys, `#` comments after flow `[ip]`, CRLF, and tab-as-indent still join `disagree hostAliases.ip` (indent subset, already paid).

### Other declared leftovers (unchanged)

- Go tags and YAML keys remain **separate rows** (`HostAlias.IP` and `hostAliases.ip`), not one merged object. Documented `FILE.go FILE.yaml` no longer drops the YAML half.
- protobuf `opt` is printed, not a verdict (`json:"name"` + protobuf opt → `agree Item.Name`; + `omitempty` → `disagree`).
- Tabs inside a json name (`json:"na<TAB>me"`) vs `listMapKey=name` is `missing` (wire name is not `name`).
- Exit 0 without `--check` still includes `disagree` (Unix filter via `--check` exists). Owned 052 without the flag: `disagree_n 2` rc=0. With `--check`: same rows, rc=1. 400 list+elem pairs: 400 `disagree` rows, rc=0, no cap.

Other declared ceilings still hold: field-line regex (generics / type aliases / `*[]T`); `+patchMergeKey` without `+listMapKey` is `join none` rc=0 (no identity hint); `+listMapKey` prose / `/* +listMapKey */` is `unparsed` rc=2; array-schema `required: [ip]` is still `disagree` (item-level only).

---

## TRANSFER CRDs (same files as `TRANSFER_tagjoin_crd.md`)

| file | result | keys |
| --- | --- | --- |
| `kubernetes.crossplane.io_objects.yaml` | TRANSFER agree_n 1, unparsed_n 0, rc=0; `--check` rc=0 | `conditions.type` required |
| `px.dev_viziers.yaml` | TRANSFER agree_n 1; `--check` rc=0 | `claims.name` required |
| `monitoring.coreos.com_servicemonitors.yaml` | TRANSFER agree_n 5; `--check` rc=0 | `bindings.{group,resource,name,namespace}`, `conditions.type` |
| `gateway.networking.k8s.io_httproutes.yaml` | TRANSFER agree_n 5 (22 file hits) | `headers.name`, `add.name`, `set.name`, `queryParams.name`, `conditions.type` |
| `cert-manager.io_certificates.yaml` | TRANSFER agree_n 1 (4 file hits) | `conditions.type` |
| `apis__apps__v1_openapi.json` | TRANSFER disagree_n 2, agree_n 16; `--check` rc=1 | **`hostAliases.ip` / `imagePullSecrets.name` disagree** (specimen-052 keys) |
| `k8s-core-v1-types.go` | TRANSFER disagree_n 4, agree_n 25, missing_n 1; `--check` rc=1 | `LocalObjectReference.Name`, `HostAlias.IP`, `PodIP.IP`, `ObjectReference.Name`; `Condition.type` missing (metav1 lives in another file) |
| `argoproj.io_applications.yaml` | `join none` rc=0 | zero list-map hits; not this miss |

Crossplane / pixie / ServiceMonitor are still not `unparsed	x-kubernetes-list-map-keys`.

---

## Primitive

Reality-stripped operation: line-regex Go tags; collect `+listMapKey` on slice fields; look up that string as a **case-sensitive json wire name**; `disagree` iff omitempty/omitzero/`+optional` and no `+default`. Plus an indent YAML subset that keeps siblings after `|-` and `versions:` sequence children, JSON `json.loads` when the text starts with `{`/`[`, local `#/` `$ref` / `allOf`, and a regex over apply-error `properties[list].items.properties[key]`. Multiple paths are parsed separately, then joins merge. Duplicate YAML/JSON list-map nodes collapse on `(list_name, key)` first-wins.

Nearest ordinary workflow: `grep omitempty` and `grep listMapKey` in one Go file, then a hand look at the element type. After mutate-3 that join is still the useful delta. Pass 4 did not restore `description: |-` / case-fold / Go-first YAML-drop.

Lost if the **CLI** vanishes: naming which identity key is optional — owned `HostAlias.IP` / `LocalObjectReference.Name`, unseen `containerPort`, real CRD `conditions.type` / pixie `claims.name` / ServiceMonitor `bindings.*`, OpenAPI `hostAliases.ip` still `disagree`, `json:",omitempty"` as empty name + omitempty, `json:"-"` as not a key, `listMapKey=IP` vs `json:"ip"` as `missing`, `--check` rc=1, `FILE.go FILE.yaml` both halves.

Lost if the **question** is a full YAML document with anchors/aliases/flow maps, or one merged HostAlias.IP ↔ hostAliases.ip object, or a version-diff of mixed optionality across `spec.versions`: the indent subset `unparsed`s, names the definition, or first-wins. Grep of `x-kubernetes-list-map-keys` still shows the keys. That is the declared ceiling, not the TRANSFER miss, and not a leftover-identity lie the indent subset should cut without becoming a CRD generator.

That is why this is **KEEP**, not KILL and not MUTATE: Honor-KILL regressions did not fire; the join still names which identity key is optional on owned 052, on v1.30.0 types.go, and on the CRDs that were `unparsed` before mutate-3; remaining leftovers require a YAML parser or a CRD version-diff.

Not FIX: remaining leftovers are the indent-subset / TSV / `--check` ceiling written in MUTATE.md, still unbuilt, still honest (`unparsed` rather than false `agree` on aliases).

Not a required MUTATE: growing a YAML parser, a Go↔YAML object merge, mixed-version collision, or making protobuf `opt` a verdict would rebuild a CRD generator. Research boundary forbids that. Do not send that theater back to R1.

---

Do not merge onto `main`. Do not run controller-gen. Do not apply CRDs. Do not start jury.

---

KEEP
