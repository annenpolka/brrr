# DESTROYER pnpbuilt

Date: 2026-09-02 15:44 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pnpbuilt/pnpbuilt`

sha256 `166f92cc96d4362907a1a68df34142064d7e59f89ea2e7dc7b55f457026eb751` (3087 bytes, 98 lines). No `pnpbuilt` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-pnpbuilt/`) and was not merged. Host Python 3.14.5. `yarn` is **not on PATH** (`command -v yarn` → NONE) and **was not executed**.

Origin claim (`CANDIDATE.md` / harvest `hdd-pnpstale` / specimen-089 leftover already-built storedBuildState after unplugged tree gone): leftover_built = stored_hash AND NOT unplugged_ready on caller-labeled `stored_hash` / `unplugged_ready` TSV flags. grep of the locator hits build-state; the miss is absent `.ready`. Kind: USEFUL_COMPOSITION. Owned packet: Case C after `rm -rf .yarn/unplugged`, leftover hash still matches, no YN0007, native binary absent. Rejected: invented yarn install/rebuild transcripts. Constraint: owned labeled excerpts. No yarn.

Happy path is real. Unit tests 4/4 pass (`python3 -m unittest discover -s tests -v` → `Ran 4 tests in 0.103s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 579 bytes). That is not enough.

This candidate is a **THIN_WRAPPER** of two caller flags: `yn_in(stored_hash) and not yn_in(unplugged_ready)`. `inspect()` never reads a build-state.yml map, never hashes path strings, never `ls`es `.yarn/unplugged/.../.ready`, never looks at `binary` when it decides leftover. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on 29/29 parse-success host cases (`stdout_eq=True`). A python one-liner of the two yes-set flags matches the `leftover_built` row and rc on **225/225** non-empty token pairs and on owned leftover / built / never. awk of `$1=="stored_hash"` vs `$1=="unplugged_ready"` matches the three load-bearing columns on 26/30 (empty field / extra tab / leading tab / CRLF are the parser's `strip()`, not a PnP walker). Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pnpbuilt/pnpbuilt
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pnpbuilt/fixtures
S089=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-089
```

No merge onto `main`. No yarn. Do not grow a `build-state.yml` / `storedBuildState` / unplugged `.ready` walker to escape THIN_WRAPPER. Do not send yarn theater back to R1. First HARVEST is not protection. Same shape as Honor-KILLed peerleft / sumext: leftover = in A not in B on caller-labeled flags.

---

## What still works

Owned leftover, intact built, never-built, unseen `widget` copies of those three, and any other TSV whose rows are already `stored_hash yes|true|1|present` vs `unplugged_ready` the same set, **when the question is only whether the first flag is in the yes-set and the second is not**.

```bash
python3 "$CLI" "$FIX/089-leftover.rec"
echo rc=$?
```

```text
locator	@sentry/cli@npm:1.62.0
stored_hash	yes
unplugged_ready	no
binary	no
leftover_built	yes
identity	leftover-built
rc=1
```

119 bytes. Stderr empty. Owned built: `stored_hash	yes` / `unplugged_ready	yes` / leftover no / `identity	built`, rc=0, 111 bytes. Owned never: both flags no / leftover no / `identity	never-built`, rc=0, 114 bytes. Unseen `widget@npm:0.1.0` leftover: same six rows with that locator, leftover yes, rc=1.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode locator `依存@npm:1`: leftover yes, rc=1. 10000 comment lines plus leftover flags: leftover yes, rc=1, stdout **98** bytes (locator `x`), ~0.026s. Same 10000 plus both flags yes: leftover no, rc=0, 90 bytes, ~0.026s. Missing path / directory / invalid UTF-8 / BOM / binary NUL / unknown field / origin split / YAML / JSON: `pnpbuilt: …` rc=1. No args / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `stored and not ready` already does on two caller-labeled booleans.

---

## Implementation

`inspect()` in full:

```python
def inspect(fields: dict[str, str]) -> dict:
    stored = yn_in(fields.get("stored_hash") or "")
    ready = yn_in(fields.get("unplugged_ready") or "")
    binary = yn_in(fields.get("binary") or "")
    leftover = stored and not ready
    identity = "leftover-built" if leftover else ("built" if stored and ready else ("never-built" if not stored else "ready-without-hash"))
    return {
        "locator": fields["locator"],
        "stored_hash": stored,
        "unplugged_ready": ready,
        "binary": binary,
        "leftover_built": leftover,
        "identity": identity,
    }
```

`inspect.co_names` is `('yn_in', 'get')`. `inspect.co_varnames` is `('fields', 'stored', 'ready', 'binary', 'leftover', 'identity')`. `inspect.co_consts` includes `'leftover-built'`, `'built'`, `'never-built'`, `'ready-without-hash'`. dis: three `yn_in` calls (`stored_hash`, `unplugged_ready`, `binary`), then `stored` AND `UNARY_NOT` of `ready`. There is no prefix, no sha512, no YAML, no `.ready` path, no unplugged tree, no YN0007.

`yn_in` is `val in {"yes", "true", "1", "present"}`. `parse_record` accepts keys `locator` / `stored_hash` / `unplugged_ready` / `binary` only. First tab splits key/value; `rest.strip()` is the value. Unknown keys raise. `locator` is required and echoed. leftover never reads `binary`. leftover never reads the locator except to reprint it.

When leftover is yes, `stored_hash` is always yes and `unplugged_ready` is always no. Tests never hit binary-as-spectator, actual hash tokens, ready-without-hash, missing ready, extra tabs, origin bytes, stdin, or the identity matrix. Four tests: owned leftover, owned built, owned never, missing file.

---

## Attacks

### 1. THIN_WRAPPER of `stored and not ready`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on the harvest shapes:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | stored | ready |
| --- | ---: | ---: | --- | --- | --- | --- |
| owned leftover | 1 | 1 | True | True | True | False |
| owned built | 0 | 0 | True | False | True | True |
| owned never | 0 | 0 | True | False | False | False |
| unseen widget leftover | 1 | 1 | True | True | True | False |
| unseen widget built | 0 | 0 | True | False | True | True |
| unseen widget never | 0 | 0 | True | False | False | False |
| stdin leftover | 1 | 1 | True | True | True | False |

Python one-liner, no `inspect` import, labeled flags only:

```bash
python3 -c '
import sys
YES={"yes","true","1","present"}
fields={}
for raw in open(sys.argv[1], encoding="utf-8"):
    line=raw.strip()
    if not line or line.startswith("#") or "\t" not in line: continue
    k,r=line.split("\t",1)
    fields[k.strip()]=r.strip()
stored=fields.get("stored_hash","") in YES
ready=fields.get("unplugged_ready","") in YES
print("stored_hash", stored)
print("unplugged_ready", ready)
print("leftover", stored and not ready)
' "$FIX/089-leftover.rec"
```

```text
stored_hash True
unplugged_ready False
leftover True
```

Same membership function vs the CLI `leftover_built` row and rc: owned leftover / built / never match. Token grid of 16×16 yn-ish strings: **225/225** non-empty pairs match; the 31 empty-field pairs are `expected key<TAB>value` because `line.strip()` eats a trailing tab (`stored_hash\t` becomes `stored_hash`). That is not a PnP walker.

awk of the three load-bearing columns, without `binary` / `identity` / `locator`:

```awk
BEGIN{FS="\t"}
/^#/ {next}
NF<2 {next}
{
  k=$1; v=$2
  gsub(/^[ \t]+|[ \t]+$/, "", k)
  gsub(/^[ \t]+|[ \t]+$/, "", v)
  f[k]=v
}
END{
  stored = (f["stored_hash"]=="yes" || f["stored_hash"]=="true" || f["stored_hash"]=="1" || f["stored_hash"]=="present")
  ready = (f["unplugged_ready"]=="yes" || f["unplugged_ready"]=="true" || f["unplugged_ready"]=="1" || f["unplugged_ready"]=="present")
  leftover = stored && !ready
  printf "stored_hash\t%s\n", stored?"yes":"no"
  printf "unplugged_ready\t%s\n", ready?"yes":"no"
  printf "leftover_built\t%s\n", leftover?"yes":"no"
}
```

owned leftover / built / never / unseen / true-false / 1-0 / present-absent / missing-ready / locator-only / both-yes / both-no / unicode / huge / duplicates: `awk_eq_cli_loadbearing=True`. 26/30 overall. Hash column is not in the awk. `binary` is not in the awk. They do not vote. Naive awk misses extra-tab (CLI keeps `yes\textra`, which is not in the yes-set), leading tab (CLI `strip()`s it into `yes`; awk `$2` is empty), CRLF (version field keeps `\r`), and empty field (CLI parse error). That is not an unplugged tree.

Nearest ordinary workflow, host-executed:

```bash
grep -n '@sentry/cli' "$FIX/089-leftover.rec"
grep -n '@sentry/cli' "$FIX/089-built.rec"
grep -n '@sentry/cli' "$FIX/089-never.rec"
ls "$FIX"/**/.ready
ls "$FIX"/**/unplugged
```

```text
2:locator	@sentry/cli@npm:1.62.0
2:locator	@sentry/cli@npm:1.62.0
2:locator	@sentry/cli@npm:1.62.0
ls .ready in fixtures []
ls unplugged []
```

`demo.sh` says “grep locator in build-state; ls unplugged .ready”. grep of the locator hits leftover, built, **and** never because the caller wrote the locator on all three. There is no `.ready` file and no unplugged tree in the fixtures. leftover is whether they also wrote `stored_hash	yes` and `unplugged_ready	no`.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`binary`, `identity`) to escape classification. `binary` is `yn_in` of a spectator flag. leftover does not read it. `identity` is a sticker for the same two bits.

### 2. `binary` is a spectator

Host-executed, leftover flags plus `binary	yes`:

```text
locator	@sentry/cli@npm:1.62.0
stored_hash	yes
unplugged_ready	no
binary	yes
leftover_built	yes
identity	leftover-built
rc=1
```

Same leftover yes, rc=1, with no `binary` field at all (`binary	no` is the default). Intact built with `binary	no`: leftover no, `identity	built`, rc=0. The harvest leftover is “native binary absent after unplug-delete.” This CLI reprints a caller flag named `binary`. Changing it never changes leftover.

When leftover is yes, `binary` may be yes or no. There is a TSV in which leftover is yes and `binary` is no (owned leftover). `binary` is not evidence that sentry-cli was missing.

### 3. Actual hash is not `stored_hash`

Harvest leftover is a leftover sha512 in `Project.storedBuildState`. Host-executed against `stored_hash	sha512-deadbeef` / `unplugged_ready	no`:

```text
locator	@sentry/cli@npm:1.62.0
stored_hash	no
unplugged_ready	no
binary	no
leftover_built	no
identity	never-built
rc=0
```

The hash bytes are the **value** token. They are not in `{yes, true, 1, present}`. leftover no. Same for `stored_hash	sha512-deadbeef` / `unplugged_ready	yes`: leftover no, identity `never-built` even with ready yes. `YES` / `Yes` / `hash` / `on` / `-`: leftover no. `true` / `1` / `present` vs a non-yes ready: leftover yes. The caller must already have reduced a storedBuildState row to `stored_hash	yes`. That reduction is the product. The CLI reprints it.

### 4. `ready-without-hash` is dead; ready-without-hash is labeled `never-built`

`inspect` names four identities. Host-executed 2×2×2 matrix of yes/no on stored / ready / binary:

| stored | ready | leftover | identity | rc |
| --- | --- | --- | --- | ---: |
| yes | yes | no | built | 0 |
| yes | no | yes | leftover-built | 1 |
| no | yes | no | never-built | 0 |
| no | no | no | never-built | 0 |

`binary` never changes leftover or identity. Seen identity labels: `{leftover-built, built, never-built}`. `ready-without-hash` is in `co_consts` and is **unreachable**: leftover is `stored and not ready`, so the branch `not leftover and stored and not (stored and ready)` cannot fire. `stored=no` / `ready=yes` (the identity the string claims to name) prints `identity	never-built`, leftover no, rc=0.

Identity is not a third class. It is a sticker for the two flags.

### 5. Missing ready still leftover; missing stored is never-built

`locator	x` / `stored_hash	yes` and no `unplugged_ready` row: leftover yes, `unplugged_ready	no`, rc=1. The `.ready` side can be omitted and leftover still harvests. `/dev/null` is not a valid record (`need locator`). Locator-only: leftover no, identity `never-built`, rc=0.

`locator	x` / `unplugged_ready	no` and no `stored_hash`: leftover no, identity `never-built`, rc=0. Duplicate `stored_hash` last-wins (`yes` then `no` → leftover no; `no` then `yes` → leftover yes).

Swap of the two harvest flags is not a thing this CLI does: there is one record, not two files. Directional leftover is still “A is yes-set, B is not.”

### 6. Extra tabs; empty field; stdin

`parse_record` takes `rest.strip()` after the first tab. Extra columns after `yes` stay in the value: `stored_hash	yes	extra` → token `yes\textra` → not in the yes-set → leftover no, identity `never-built`, rc=0. Replica `stdout_eq=True`. awk `$2` is `yes` and disagrees. The leftover bit still follows `yn_in`.

An extra tab **before** the value (`stored_hash\t\tyes`): `strip()` eats the leading tab; token is `yes`; leftover yes, rc=1. Empty value (`stored_hash\t\n`): `line.strip()` eats the trailing tab; `expected key<TAB>value`, rc=1, no TSV.

`-` is stdin. Owned leftover body on the pipe: leftover TSV, rc=1, replica `stdout_eq=True`. Empty stdin / `-` with no pipe: `need locator`, rc=1. `/dev/stdin` leftover: leftover yes, rc=1. Fine as a one-file tool. The bit is still two caller-labeled flags.

Argv-less / extra positional: argparse rc=2, pipe ignored.

### 7. Origin bytes refuse; grep locator vs ls `.ready` is already the fixture

Specimen `leftover_identity_split.txt` as record: `expected key<TAB>value`, rc=1. YAML-ish `"@sentry/cli@npm:1.62.0": "sha512-abc"`: same parse error, rc=1. JSON `{"storedBuildState":…}`: same. `packageLocation	unplugged`: `unknown field 'packageLocation'`. `Locator	x`: `unknown field 'Locator'`. UTF-8 BOM: `unknown field '\ufefflocator'`. Embedded NUL: `unknown field '\x00stored_hash'`. Invalid UTF-8: codec error, rc=1.

The harvest presence test is grep of the locator in build-state plus `ls` of `.yarn/unplugged/.../.ready`. Host-executed, those origin bytes are not TSV. leftover no (no TSV). The caller must already have split the hash map vs the missing `.ready` into `stored_hash` vs `unplugged_ready` rows. That split is the product. The CLI reprints it.

### 8. Huge dump; still two flags

10000 `# pad` lines plus leftover flags: leftover yes, rc=1, stdout **98** bytes, 0.026s. Same 10000 plus both flags yes: leftover no, rc=0, 90 bytes, 0.026s. No cap. No locators dumped. The useful bit is still `stored and not ready`.

Tests never hit duplicates, origin, extra tabs, stdin, binary spectator, actual hashes, ready-without-hash, or missing ready. They do hit missing file. Happy path is real. That is not enough.

---

## Primitive

Reality-stripped operation: parse one TSV file of `locator` plus optional `stored_hash` / `unplugged_ready` / `binary` flags; leftover iff `stored_hash` is in `{yes,true,1,present}` and `unplugged_ready` is not; print six TSV rows; rc=1 iff that bit. `binary` is a spectator boolean. `identity` labels the same two bits (`ready-without-hash` unreachable).

Nearest ordinary workflow: `grep '^stored_hash'` vs `grep '^unplugged_ready'` on the flags the caller already labeled, or `python3 -c 'print(stored and not ready)'`, or the awk above. Observable capability lost if pnpbuilt vanishes: **none**. The excerpt already is the input. The leftover-vs-ready join is still a hand comparison after the caller typed `stored_hash	yes` vs `unplugged_ready	no`. grep of the locator hits leftover, built, and never because all three fixtures contain the locator. `ls .ready` finds nothing in the fixtures.

That is why this is KILL, not MUTATE. The *question* (after `rm -rf .yarn/unplugged`, is this locator still a leftover already-built `storedBuildState` hash while `.ready` / the native binary are gone, or omitted the way never-built was — grep hits the locator, the miss is `.ready`) is a real debugging object. This embodiment does not ask it of build-state.yml or an unplugged tree. It asks `stored and not ready` on caller-labeled tokens. Adding a `storedBuildState` / `getBuildHash` / `.ready` walk, or ingesting yarn install-state, would be implementing the yarn theater the harvest rejected, and would be a new harvest, not a patch of this 98-line `and not`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Honor-KILLed peerleft is leftover = in B not in A on two caller-labeled regions. Honor-KILLed sumext is leftover = in extension not in record on two caller-labeled regions. This is leftover = flag A and not flag B on two caller-labeled flags.

Hardcoded ceiling:

- leftover iff stored yes-set and ready not yes-set; binary / locator / identity do not vote
- leftover yes ⇒ stored_hash yes and unplugged_ready no
- leftover yes with missing ready (`stored_hash	yes` only)
- both yes / both no / neither stored: leftover no, same bit
- ready without stored: leftover no, identity `never-built` (not `ready-without-hash`)
- `ready-without-hash` is unreachable
- actual sha512 / `YES` / `hash` as stored_hash: leftover no, identity `never-built`
- `yes` / `true` / `1` / `present` are one yes-set
- extra tab after the value stays in the token and misses the yes-set; extra tab before the value is `strip()`ped
- empty field after strip is `expected key<TAB>value`
- `-` is stdin; empty stdin is `need locator`
- origin split / YAML / JSON / `packageLocation` / `Locator` / BOM / NUL refuse
- 10k-comment leftover still 98-byte sticker, ~0.026s
- rc=1 on leftover **or** parse/IO; argparse rc=2 on missing argv
- Dreamer yarn install/rebuild was rejected; this is that leftover, reduced to the harvest sentence as `and not`

Honor KILL. Dreamer ancestry is not protection.

Do not grow a yarn runner, a `build-state.yml` parser, or an unplugged `.ready` walker to escape THIN_WRAPPER. Do not merge this join onto `main`. No yarn. Do not send yarn theater back to R1.

---

KILL
