# DESTROYER patchident 2

Date: 2026-09-02 15:35 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, first-destroyer KEEP):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchident/patchident`

CLI sha256 `370dbb02110f44763c0553e7e81dffe51f2fe3ddc386b08c80a9210949c237e5` (4407 bytes, 134 lines).
Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-patchident-patchident/patchident/patchident` is byte-identical (`cmp` identical; branch `specimen-hdd/candidate-patchident-patchident`, HEAD `c35f800 ground patchident from hdd-pnpmhash harvest`). Parent `main` is `432f954`; `git cat-file -e HEAD:patchident` fails — not in that tree. Tests: `python3 -m unittest discover -s …/tests -v` → 6/6 OK, rc=0. `demo.sh` live stdout byte-identical to `demo-1.log` / `demo-2.log` (754 bytes). Host Python 3.14.5. `pnpm` is on PATH (`/opt/homebrew/bin/pnpm`) and **was not executed**. No merge onto `main`. Worktree was not edited.

Origin: harvest `hdd-pnpmhash` / specimen-085. Name which identity a `patchedDependencies` selector has: path+hash object, hash-only string, empty, or omitted. `legacy_dot_hash` empty on a string (the `.hash` miss). Kind: USEFUL_COMPOSITION. Constraint: owned two lock excerpts. No pnpm.

First destroyer (`DESTROYER_patchident.md`) **KEEP**: owned object → rc=0, hash=legacy; hash-only → rc=1, `legacy_dot_hash -`; empty string `empty`; omitted selector `omitted`. Stdin object works. Holes named then: tiny YAML subset; selector grep still hits both files; hash bytes never compared to a patch file. That KEEP said a later destroyer may KILL if it is still two greps plus a sticker. First KEEP is not protection. This is that destroyer.

Job `job-0358` kill_condition: Honor KILL if two greps. Competing harvest `candidate-patchid` of the same specimen was Honor-KILLed this run (`DESTROYER_patchid.md` / `fossils/patchid.md`) as THIN_WRAPPER of YAML kind switch (mapping vs string). Sibling KEEP does not protect this object; sibling KILL does not need a third lockfile CLI.

This candidate is a **THIN_WRAPPER of YAML kind switch (mapping vs string) / two greps plus a sticker**. Identity is whether the selector line is `sel:`, `sel: value`, `sel: ""`, or missing, plus whether a nested `path`/`hash` line upgraded the empty mapping. `legacy_dot_hash` is `hash` iff identity is object else `-`. rc=0 iff object (sibling `patchid` used rc=0 iff hash-only — polarity sticker). Host replica of `parse_lock` + `inspect` is byte-identical to the CLI on owned object/hash-only/empty/omitted. An independent indent-2 mapping-vs-string sticker matches full stdout+rc on those owned four and on the specimen-085 files (`cmp` identical). Hash bytes are unused. A second selector in the same block is `unknown field`, rc=1, no TSV. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchident/patchident
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchident/fixtures
S085=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-085/files
```

Host-executed against the archive only. No pnpm. Do not grow a pnpm lockfile parser to escape THIN_WRAPPER. Do not send pnpm theater back to R1. Do not merge onto `main`. Distinct from specimen-068.

---

## What still works

Owned 085 object: `identity object` / `legacy_dot_hash fixture-patch-hash` / rc=0.

Hash-only: `identity hash-only` / `legacy_dot_hash -` / rc=1. Empty string: `identity empty` / rc=1. Missing selector: `identity omitted` / rc=1. Stdin object/hash/empty work with `-`. Missing path rc=1. Fixtures equal the owned packet (`cmp` rc=0). Demos identical. Tests 6/6.

```bash
python3 "$CLI" "$S085/patcheddeps.object.yaml" --selector "express@4.18.1"; echo rc=$?
python3 "$CLI" "$S085/patcheddeps.hash.yaml" --selector "express@4.18.1"; echo rc=$?
python3 "$CLI" "$FIX/patcheddeps.empty.yaml" --selector "express@4.18.1"; echo rc=$?
python3 "$CLI" "$S085/patcheddeps.hash.yaml" --selector "missing-package@1.0.0"; echo rc=$?
```

```text
selector	express@4.18.1
identity	object
shape	object
path	patches/express@4.18.1.patch
hash	fixture-patch-hash
legacy_dot_hash	fixture-patch-hash
rc=0

selector	express@4.18.1
identity	hash-only
shape	string
path	-
hash	fixture-patch-hash
legacy_dot_hash	-
rc=1

selector	express@4.18.1
identity	empty
shape	empty
path	-
hash	-
legacy_dot_hash	-
rc=1

selector	missing-package@1.0.0
identity	omitted
shape	omitted
path	-
hash	-
legacy_dot_hash	-
rc=1
```

That is the whole useful surface. It is also what a mapping-vs-string look at the selector line already does, plus labels.

---

## Implementation

```python
# selector line (any non-field indent after patchedDependencies:):
if val == "":
    entries[sel] = {"shape": "empty", "path": "", "hash": ""}
else:
    entries[sel] = {"shape": "string", "path": "", "hash": val}
# any later line that startswith(" ") with current set:
#   path/hash → shape "object"; else unknown field rc=1
# inspect: object → identity object, legacy=hash
#          empty or hash=="" → empty, legacy=""
#          else hash-only, legacy=""   # originalPatchFile?.hash on a string
# main: return 0 if identity == "object" else 1
```

`inspect` names: `EMPTY`, `dict`, `entries`, `hash_v`, `identity`, `legacy`, `path`, `rec`, `selector`, `shape`, `str`. No hash compare. No patch file. No lockfileVersion. Source has no `pnpm`, no `hashlib`.

`demo.sh` already names the nearest operation: `grep the selector` / `grep express@4.18.1 hits object and hash-only lock excerpts`.

---

## Attacks

### 1. THIN_WRAPPER of two greps plus a sticker

Nearest ordinary workflow, host-executed:

```bash
grep -n "express@4.18.1" "$S085/patcheddeps.object.yaml" "$S085/patcheddeps.hash.yaml"
grep -E '^  express@4\.18\.1:$' "$S085/patcheddeps.object.yaml"; echo mapping_object=$?
grep -E '^  express@4\.18\.1:$' "$S085/patcheddeps.hash.yaml"; echo mapping_hash=$?
grep -E '^  express@4\.18\.1: .+' "$S085/patcheddeps.hash.yaml"; echo string_hash=$?
grep -E '^  express@4\.18\.1: .+' "$S085/patcheddeps.object.yaml"; echo string_object=$?
grep -E '^  express@4\.18\.1: ""$' "$FIX/patcheddeps.empty.yaml"; echo empty=$?
grep -E '^  missing-package@1\.0\.0:' "$S085/patcheddeps.hash.yaml"; echo omitted=$?
```

```text
patcheddeps.object.yaml:2:  express@4.18.1:
patcheddeps.object.yaml:3:    path: patches/express@4.18.1.patch
patcheddeps.hash.yaml:2:  express@4.18.1: fixture-patch-hash
mapping_object=0
mapping_hash=1
string_hash=0
string_object=1
empty=0
omitted=1
```

grep of the selector hits both shapes (object also hits the path line). The CLI's `object` is “selector line ends with `:` and a nested `path`/`hash` line exists”. `hash-only` is “same line has a nonempty scalar”. `empty` is `sel: ""` / `sel: ''` / bare `sel:` with no nested fields. `omitted` is no indent-2 hit.

Sticker on those four owned files (indent-2 mapping vs string + nested path/hash copy + `legacy_dot_hash = hash iff object else -` + `rc=0 iff object`) is **byte-identical** to CLI stdout+rc on fixture object / hash / empty / omitted and on specimen-085 object / hash (`eq True` 6/6).

`legacy_dot_hash` is not a second identity. It is the object-hash copied, or `-`. Constitution: a THIN_WRAPPER does not gain extra TSV rows (`shape`, `legacy_dot_hash`) to escape classification. Those rows are labels on the kind switch.

### 2. Replica matches stdout+rc

Independent reconstruction of `parse_lock` + `inspect` + `format_report` + `rc = 0 iff object` (no import of the module) is **byte-identical** to the CLI on owned object / hash-only / empty / omitted, hash-mutated AAA object and AAA hash-only, path-only, hash-field-only, comments, CRLF, flow `{path, hash}` as a scalar, YAML `null` / `~` tokens, tab-indent, four-space selector, empty single quotes, trailing-space colon, specimen-085 files.

Mismatches are not hash identity. They are parse refusals of a second indented selector, or a sticker that does not swallow `packages:` after the block:

- two selectors (`express@4.18.1: hash-short` then `express@4.18.10: hash-long`): CLI `unknown field 'express@4.18.10'` rc=1, no TSV
- duplicate last-wins (`sel: first` then `sel:` + nested path/hash): `unknown field 'express@4.18.1'` rc=1
- lockfileVersion + `packages:` after the block: `unknown field '/express@4.18.1'` rc=1
- 5000 other selectors then the target: `unknown field 'other@1'` rc=1
- two objects in one block: `unknown field 'lodash@4.17.21'` rc=1 even when querying the first selector

Once `current` is set, every later `startswith(" ")` line is a `path`/`hash` field of that one selector. A real lockfile with two `patchedDependencies` entries cannot be named. That is not a remainder to MUTATE. Growing indent==2 vs indent>=4, or a YAML loader, is a pnpm lockfile parser.

Flow mapping is hash-only with `hash	{path: p, hash: h}` rc=1. A YAML parser would say mapping. This wrapper never parsed YAML; it saw a nonempty same-line scalar.

### 3. Hashes unused. `.hash` on a string is the kind switch

```text
object hash: AAA     → identity object    rc=0   legacy AAA
hash-only hash: AAA  → identity hash-only rc=1   legacy -
```

Identity and rc are stable when the hash bytes change (`HASH_UNUSED_kind_stable` all True). `legacy_dot_hash` on a string is always `-`, including when the scalar is `AAA`, `null`, `~`, or `{path: p, hash: h}`. That is “`originalPatchFile?.hash` on a string is empty” restated as YAML node kind. There is no compare to a `.patch` file. There is no `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH`.

Path-only object: `identity object` / `hash -` / `legacy_dot_hash -` / rc=0. Hash-field-only: `identity object` / `legacy_dot_hash onlyhash` / rc=0. Bare `sel:` with no body: `identity empty` / rc=1 — same as `sel: ""`. The harvest labels are the YAML node kind of a line the caller already supplied.

### 4. Selector prefix. Quotes stay in the NAME

Exact match only. On owned object and hash-only files:

| `--selector` | identity |
| --- | --- |
| `express` | omitted |
| `express@4.18` | omitted |
| `express@4.18.1` | object / hash-only |
| `express@4.18.10` | omitted |
| `patches/express@4.18.1.patch` | omitted |
| `fixture-patch-hash` | omitted |

Quoted `'express@4.18.1': abc` with `--selector express@4.18.1`: omitted. Same file with `--selector "'express@4.18.1'"`: hash-only / hash abc. Selector quotes are not stripped. Prefix is not a parse of the selector.

### 5. Stdin, missing file, BOM

`-` reads stdin (object rc=0, hash-only rc=1, empty rc=1). File argv ignores piped body (`hash` stays `fixture-patch-hash`). `/dev/stdin` and symlink work because `Path.read_text` opens the node. `/no/such.yaml` → `patchident: [Errno 2] No such file or directory: '/no/such.yaml'` rc=1, no TSV. Directory → `Is a directory` rc=1. No args / missing `--selector`: argparse rc=2.

BOM before `patchedDependencies:` → omitted (the header no longer `startswith("patchedDependencies:")`). Empty file / comments-only → omitted rc=1, not a parse error. Extra unknown field → `unknown field 'extra'` rc=1, no TSV. `|` multiline → `expected path/hash field` rc=1. `patchedDependencies: leftover` still enters the block (`startswith`); hash-only of the following indent-2 line still harvests.

### 6. Invalid YAML upgrades; tab indent is a selector

`sel: first` then indented `path: sneaky` (invalid YAML): CLI `identity object` / `path sneaky` / `hash first` / `legacy_dot_hash first` / rc=0. Kind-switch of the indent-2 line says hash-only; nested `path` upgrades it. Indent state machine, not a lockfile reader.

Tab-indented selector: `startswith(" ")` fails, so the stripped line is parsed as a selector → hash-only `abc` rc=1. Four-space selector with `current is None` is also a selector (hash-only). Sibling `patchid` required indent==2 and refused both. Neither is YAML.

### 7. Tests 6/6 is not enough. rc polarity is a sticker

Owned object, hash-only, empty, omitted, stdin object, missing file: that is the test file. Those six already are the YAML kind switch plus IO. rc=0 only for object is a sticker (Honor-KILLed `patchid` uses rc=0 for hash-only on the same two fixtures). Demos identical. Constitution: a THIN_WRAPPER does not gain a pnpm lockfile parser to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection once the KEEP surface is shown to be two greps plus labels.

---

## Primitive

Reality-stripped operation: scan a caller-supplied YAML excerpt after a line that `startswith("patchedDependencies:")`; take one selector line; if a later space-indented `path`/`hash` appears call it object and copy those strings; if the same line has `""` call it empty; if it has any other scalar call it hash-only; if missing call it omitted; print `legacy_dot_hash` as the object hash else `-`; rc=0 iff object. A second selector is `unknown field`.

Nearest ordinary workflow (owned packet, also `demo.sh`):

```text
grep express@4.18.1
grep -E '^  express@4\.18\.1:$'          # mapping
grep -E '^  express@4\.18\.1: .+'        # string
# sticker: object if mapping+nested path/hash; hash-only if scalar; empty if ""; omitted if miss
#          legacy_dot_hash = hash if object else -
```

On specimen-085 that pair is: v9 `{path, hash}` vs v11 hash string, and `originalPatchFile?.hash` empty on a string. patchident’s load-bearing claim is that naming `identity` / `legacy_dot_hash` is a join those two greps do not already contain.

It is not. The statuses are labels. Hash bytes do not vote. Two selectors refuse. Mounting pnpm / comparing a `.patch` file is out of scope and was not executed.

Observable capability lost if patchident vanishes: **none**. The harvest excerpts already are that classification. Sibling `patchid` already named the same kind switch (Honor-KILLed). Do not mutate patchident into a YAML loader or a pnpm lockfile reader to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.” Do not mint a third patchedDependencies CLI.

That is why this is KILL, not MUTATE. The *question* (did the lock contain a path+hash object or a bare hash string, so `.hash` on a string is empty) is a real debugging object. This embodiment does not ask it of pnpm, a patch file, or even of two selectors. It asks whether one caller-supplied YAML line is a mapping or a string. First-destroyer KEEP is not protection once that KEEP is shown to be two greps plus a sticker.

Hardcoded ceiling:

- identity is YAML node shape of one selector line, not pnpm lockfile v9 vs v11
- `legacy_dot_hash` is object-hash else `-`; hashes unused; no patch-file compare; no frozen-install mismatch
- second selector / after-block `packages:` → `unknown field` rc=1, no TSV
- selector is exact string; quotes stay in the NAME; prefixes omitted
- flow mapping / `null` / `~` are hash-only scalars
- bare `sel:` is empty, not object, until a nested path/hash upgrades it
- invalid `sel: scalar` plus nested `path` upgrades to object
- tab indent and four-space selector are selectors, not mappings
- BOM skips the block → omitted
- rc=0 iff object; hash-only/empty/omitted/IO share rc=1 (sibling patchid inverted the sticker)
- Dreamer lockfile-inspector was rejected; this is that inspector, reduced to the harvest sentence as mapping vs string on the owned excerpts

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection. Do not grow a pnpm lockfile parser to escape THIN_WRAPPER. Do not send pnpm theater back to R1. Do not merge onto `main`. Do not merge onto `patchid`.

Archive stays under `lineages/candidate-patchident/`.

KILL
