# DESTROYER patchid

Date: 2026-09-02 15:25 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-patchid/patchid`

sha256 `b20de3e8dadf6d19a68c117bc4dbdd690eed1d0f3f1e5b3721b83db84d366b53` (4479 bytes).
Archive untracked under RUN_DIR (`?? lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchid/`).
Parent `main` coordinator-only; not merged. `pnpm` is on PATH (`/opt/homebrew/bin/pnpm`) and **was not executed**.

Origin (`CANDIDATE.md` / harvest `hdd-pnpmhash` / specimen-085): name which identity
`patchedDependencies` contained for a selector — path+hash object, hash-only string,
empty hash, or omitted. grep of the selector hits both YAML shapes. Kind:
USEFUL_COMPOSITION. Rejected: invented lockfile-inspector. Constraint: owned two
lock excerpts. No pnpm.

Tests 5/5. `python3 -m unittest discover -s tests -v` → `Ran 5 tests in 0.143s` `OK`.
`demo.sh` live stdout byte-identical to `demo-1.log` / `demo-2.log` (`cmp` rc=0, 609 bytes).
Happy path is real. That is not enough.

This candidate is a **THIN_WRAPPER** of YAML kind switch (mapping vs string) on
caller-supplied lock excerpts. Kind is whether the selector line is `sel:` or
`sel: value` or `sel: ""` or missing. Hash bytes are never compared to a patch
file. Host replica of `parse_patched` + `inspect` is byte-identical to the CLI
on owned object/hash-only/empty/omitted and on every other parseable case tried.
An independent indent-2 kind-switch replica matches kind+rc on those owned four.
`grep -E '^  express@4\.18\.1:$'` vs `grep -E '^  express@4\.18\.1: .+'` is the
load-bearing bit. Job kill_condition: `thin YAML kind switch`. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchid/patchid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-patchid/fixtures
S085=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-085/files
```

No pnpm. Do not grow a pnpm lockfile parser to escape THIN_WRAPPER. Do not send
pnpm theater back to R1. First HARVEST_NOW is not protection. Sibling
`DESTROYER_patchident.md KEEP` is a different archive; it does not protect this
object. Distinct from specimen-068.

## What still works

Owned 085 object: `kind object` / `has_path yes` / `has_hash yes` / rc=1.

Hash-only: `kind hash-only` / rc=0. Empty string: `kind empty` / rc=1. Missing
selector: `kind omitted` / rc=1. Stdin object/hash/empty work with `-`. Missing
path rc=1.

```bash
python3 "$CLI" "$S085/patcheddeps.object.yaml" --selector "express@4.18.1"; echo rc=$?
python3 "$CLI" "$S085/patcheddeps.hash.yaml" --selector "express@4.18.1"; echo rc=$?
python3 "$CLI" "$S085/patcheddeps.hash.yaml" --selector "missing@1.0.0"; echo rc=$?
printf 'patchedDependencies:\n  express@4.18.1: ""\n' | python3 "$CLI" - --selector "express@4.18.1"; echo rc=$?
```

```text
selector	express@4.18.1
kind	object
path	patches/express@4.18.1.patch
hash	fixture-patch-hash
has_path	yes
has_hash	yes
rc=1

selector	express@4.18.1
kind	hash-only
path	-
hash	fixture-patch-hash
has_path	no
has_hash	yes
rc=0

selector	missing@1.0.0
kind	omitted
path	-
hash	-
has_path	no
has_hash	no
rc=1

selector	express@4.18.1
kind	empty
path	-
hash	-
has_path	no
has_hash	no
rc=1
```

Fixtures equal the owned packet (`cmp` rc=0). That is the whole useful surface.
It is also what a mapping-vs-string look at the selector line already does.

## Implementation

```python
if indent == 2 and line.endswith(":") and not line.startswith("path:") and not line.startswith("hash:"):
    entries[selector] = {"kind": "object", "path": "", "hash": ""}
elif indent == 2 and ":" in line:
    rest = line.split(":", 1)[1].strip().strip("'\"")
    entries[selector] = {"kind": "empty" if rest == "" else "hash-only", ...}
# indent >= 4 copies path/hash onto current; forces kind object
# inspect: has_path/has_hash = bool(path)/bool(hash); kind from the YAML shape
# main: return 0 if result["kind"] == "hash-only" else 1
```

`inspect` names: `bool`, `dict`, `entries`, `has_hash`, `has_path`, `rec`,
`selector`, `str`. No hash compare. No patch file. No lockfileVersion.

## Attacks

### 1. THIN_WRAPPER of YAML kind switch (mapping vs string)

Nearest ordinary workflow, host-executed:

```bash
grep -n "express@4.18.1" "$S085/patcheddeps.object.yaml" "$S085/patcheddeps.hash.yaml"
grep -E '^  express@4\.18\.1:$' "$S085/patcheddeps.object.yaml"; echo mapping_object=$?
grep -E '^  express@4\.18\.1:$' "$S085/patcheddeps.hash.yaml"; echo mapping_hash=$?
grep -E '^  express@4\.18\.1: .+' "$S085/patcheddeps.hash.yaml"; echo string_hash=$?
grep -E '^  express@4\.18\.1: .+' "$S085/patcheddeps.object.yaml"; echo string_object=$?
```

```text
patcheddeps.object.yaml:2:  express@4.18.1:
patcheddeps.object.yaml:3:    path: patches/express@4.18.1.patch
patcheddeps.hash.yaml:2:  express@4.18.1: fixture-patch-hash
mapping_object=0
mapping_hash=1
string_hash=0
string_object=1
```

grep of the selector hits both shapes (object also hits the path line). The CLI's
`object` is exactly “selector line ends with `:`”. `hash-only` is “same line has a
nonempty scalar”. `empty` is `sel: ""` / `sel: ''`. `omitted` is no indent-2 hit.
`demo.sh` already prints `nearest existing operation (grep the selector)`.

Bare `sel:` vs `sel: ""` is the same kind switch with no nested fields:

| input | kind | has_path | has_hash | rc |
| --- | --- | --- | --- | --- |
| `express@4.18.1:` | object | no | no | 1 |
| `express@4.18.1: ""` | empty | no | no | 1 |
| `express@4.18.1:   ` (trailing space, then strip) | object | no | no | 1 |

`has_path` / `has_hash` on a body-less mapping equal empty. The harvest labels
are the YAML node kind of a line the caller already supplied.

### 2. Replica matches kind+rc

Host replica of `parse_patched` + `inspect` + `format_report` + `rc = 0 iff hash-only`
is **byte-identical** to the CLI (`full_ok=True`) on owned object / hash-only /
omitted / empty, hash-mutated AAA object and AAA hash-only, quoted selectors,
lockfileVersion noise, comments, CRLF, duplicate last-wins, flow `{path, hash}`
as a scalar, YAML `null` / `~` tokens, tab-indent, prefix-pair, path-only object,
hash-field-only object, and a 5000-selector file.

Independent indent-2 kind-switch replica (no nested parse) matches **kind+rc** on
those owned four and on 23/25 extras. Mismatches are not hash identity:

- `hash-then-nested` (`sel: first` then `    path: sneaky`): CLI upgrades to
  `kind object` / `hash first` / `path sneaky` / rc=1 because indent>=4 mutates
  the current record. Kind-switch of the indent-2 line says hash-only. Invalid
  YAML, indent state machine, not a lockfile reader.
- 4-space selector: CLI `unparsed patchedDependencies line` rc=1, no TSV.
  Kind-switch says omitted. Stricter indent==2, same primitive.

Flow mapping is hash-only with `hash	{path: p, hash: h}` rc=0. A YAML parser
would say mapping. This wrapper never parsed YAML; it saw a nonempty same-line
scalar.

### 3. Hashes unused

```text
object hash: AAA     → kind object    rc=1   (same as fixture-patch-hash)
hash-only hash: AAA  → kind hash-only rc=0   (same as fixture-patch-hash)
```

Kind and rc are stable when the hash bytes change. `has_hash` is `bool(hash)`,
truthiness, not comparison to a `.patch` file. `null` and `~` are hash-only
scalars. There is no `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH`.

### 4. Selector prefix

Exact match only. On owned object and hash-only files:

| `--selector` | kind |
| --- | --- |
| `express` | omitted |
| `express@4.18` | omitted |
| `express@4.18.1` | object / hash-only |
| `express@4.18.10` | omitted |
| `patches/express@4.18.1.patch` | omitted |
| `fixture-patch-hash` | omitted |

Pair `express@4.18.1: hash-short` + `express@4.18.10: hash-long`: each exact
selector is hash-only with its own scalar; `express@4.18` omitted. Prefix is
not a parse of the selector.

### 5. Stdin, missing file

`-` reads stdin (object rc=1, hash-only rc=0, empty rc=1). File argv ignores
piped body (`hash` stays `fixture-patch-hash`). `/dev/stdin` and symlink work
because `Path.read_text` opens the node. `/no/such.yaml` →
`patchid: [Errno 2] No such file or directory: '/no/such.yaml'` rc=1, no TSV.
Directory → `Is a directory` rc=1. No args / missing `--selector`: argparse rc=2.

BOM before `patchedDependencies:` → omitted (the header line no longer equals
`patchedDependencies:`). Tab-indented selector → omitted (`startswith(" ")`
fails). Empty file / comments-only → omitted rc=1, not a parse error. Extra
unknown field → `unknown field 'extra'` rc=1, no TSV. `|` multiline → unparsed
rc=1.

### 6. Tests 5/5 is not enough

Owned object, hash-only, omitted, empty stdin, missing file: that is the test
file. Those five already are the YAML kind switch plus IO. rc=0 only for
hash-only is a sticker (sibling `patchident` uses rc=0 for object). Demos
identical. Constitution: a THIN_WRAPPER does not gain a pnpm lockfile parser
to escape classification. Worker rule: do not send THIN_WRAPPER back to R1
with “make this more novel.”

## Primitive

Reality-stripped operation: scan a caller-supplied YAML excerpt for an indent-2
`patchedDependencies` selector line; if the line ends with `:` call it object
(optionally echo nested `path`/`hash`); if the same line has `""` call it empty;
if it has any other scalar call it hash-only; if missing call it omitted; rc=0
iff hash-only.

Nearest ordinary workflow: `grep` the selector; mapping vs string is whether
that line ends with `:`. Observable capability lost if patchid vanishes: **none**.
The harvest excerpts already are that classification. Hash bytes do not vote.

Hardcoded ceiling:

- kind is YAML node shape of one indent-2 line, not pnpm lockfile v9 vs v11
- hashes unused; no patch-file compare; no frozen-install mismatch
- selector is exact string; prefixes omitted
- flow mapping / `null` / `~` are hash-only scalars
- tab indent and BOM skip the block → omitted
- indent>=4 can relabel a scalar as object
- rc=0 iff hash-only; object/empty/omitted/IO share rc=1
- Dreamer lockfile-inspector was rejected; this is that inspector, reduced to
  the harvest sentence as mapping vs string on the owned excerpts

Honor KILL. Dreamer ancestry is not protection. First HARVEST is not protection.
Do not grow a pnpm lockfile parser to escape THIN_WRAPPER. Do not send pnpm
theater back to R1. Do not merge onto `main`.

---

KILL
