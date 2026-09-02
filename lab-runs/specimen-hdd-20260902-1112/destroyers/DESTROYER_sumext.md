# DESTROYER sumext

Date: 2026-09-02 15:22 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-sumext/sumext`

sha256 `07111467a2ff0a0a5fb28c6b2888b68de153cf5ec66333fd418d34564dc73115` (3397 bytes, 97 lines). No `sumext` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-sumext/`) and was not merged. Host Python 3.14.5. `go` is on PATH (`/opt/homebrew/bin/go`) and **was not executed**. No sumdb.

Origin claim (`CANDIDATE.md` / harvest `hdd-sumdbext` / specimen-084 leftover extension vs record): leftover_identity = in_extension and not in_record on caller-labeled `record`/`extension` TSV rows. grep of the module path hits the extension line in a raw lookup body. Kind: USEFUL_COMPOSITION. Owned packet: Case B lookup of `golang.org/x/bad@v1.0.0` authenticates `golang.org/x/good` record text; extra go.sum line sits in the tree-note extension. Rejected: invented `Client.Lookup`. Constraint: owned two labeled excerpts. No go toolchain.

Happy path is real. Unit tests 7/7 pass (`python3 -m unittest discover -s tests -v` → `Ran 7 tests in 0.192s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 722 bytes). That is not enough.

This candidate is a **THIN_WRAPPER** of `(module, version) in extension and (module, version) not in record`. `inspect()` never reads a lookup body, never splits `tlog.ParseRecord`, never looks at `h1:` when it decides leftover. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on owned leftover / good / honest / unseen / missing / swap / stdin (`stdout_eq=True`). A python one-liner of labeled-region membership matches the `leftover_identity` row and rc on **29/29** host cases. awk of `$1=="record"` vs `$1=="extension"` matches the three load-bearing columns on 28/29 (CRLF is the parser's `strip()`, not a tlog). Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-sumext/sumext
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-sumext/fixtures
S084=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-084
```

No merge onto `main`. No go. Do not grow a tlog / `ParseRecord` / lookup-body parser to escape THIN_WRAPPER. Do not send go theater back to R1. First HARVEST is not protection. Same shape as Honor-KILLed peerleft: leftover = in B not in A on caller-labeled regions.

---

## What still works

Owned leftover, honest sampler, unseen both-regions, and any other TSV whose rows are already `record MODULE VERSION [hash]` vs `extension MODULE VERSION [hash]`, **when the question is only membership of `--module --version` in the extension list and not the record list**.

```bash
python3 "$CLI" "$FIX/084-leftover.rec" --module golang.org/x/bad --version v1.0.0
echo rc=$?
```

```text
module	golang.org/x/bad
version	v1.0.0
in_record	no
in_extension	yes
leftover_identity	yes
rc=1
```

91 bytes. Stderr empty. Owned good (`--module golang.org/x/good --version v1.0.0` on the same file): `in_record	yes` / `in_extension	no` / leftover no, rc=0, 91 bytes. Honest sampler: `in_record	yes` / leftover no, rc=0, 88 bytes. Unseen both: `in_record	yes` / `in_extension	yes` / leftover no, rc=0, 88 bytes. Missing module on leftover file: leftover no, both regions no, rc=0.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode module `example.com/悪い`: leftover yes, rc=1. 10000 other `record` rows (~458kB) plus leftover `golang.org/x/bad@v1.0.0` on extension: leftover yes, rc=1, stdout still 91 bytes, ~0.032s. Same 10000 plus the identity on both regions: leftover no, rc=0, ~0.029s. Missing path / directory / invalid UTF-8 / BOM / binary NUL / unknown region / origin lookup body: `sumext: …` rc=1. No args / missing `--module` / missing `--version` / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `(module, version) in extension and not in record` already does.

---

## Implementation

`inspect()` in full:

```python
def inspect(payload: dict[str, list[tuple[str, str]]], module: str, version: str) -> dict:
    key = (module, version)
    in_record = key in payload["record"]
    in_extension = key in payload["extension"]
    leftover = in_extension and not in_record
    return {
        "module": module,
        "version": version,
        "in_record": in_record,
        "in_extension": in_extension,
        "leftover_identity": leftover,
    }
```

`inspect.co_names` is `()`. `inspect.co_varnames` is `('payload', 'module', 'version', 'key', 'in_record', 'in_extension', 'leftover')`. dis: one `CONTAINS_OP (in)` on `'record'`, one on `'extension'`, then `in_extension` AND `UNARY_NOT` of `in_record`. There is no prefix, no hash, no tlog, no lookup body, no note signature.

`parse_payload` accepts keys `record` / `extension` only. First three tab fields are region, module, version. Field 4+ (the `h1:` column) is dropped. Empty / `-` module or version raise `not a legal NAME`. Unknown keys raise. leftover never reads hashes.

When leftover is yes, `in_extension` is always yes and `in_record` is always no. Tests never hit swapped labels, hash change, prefix module, origin bytes, extra tabs, same-identity different hashes, or empty first region. Seven tests: owned leftover, owned good, honest sampler, unseen both, missing module, stdin, missing file.

---

## Attacks

### 1. THIN_WRAPPER of `(mod, ver) in extension and (mod, ver) not in record`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on the harvest shapes:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | in_record | in_extension |
| --- | ---: | ---: | --- | --- | --- | --- |
| owned leftover bad | 1 | 1 | True | True | False | True |
| owned good in record | 0 | 0 | True | False | True | False |
| honest sampler | 0 | 0 | True | False | True | False |
| honest `v1.3.0/go.mod` | 0 | 0 | True | False | True | False |
| unseen both | 0 | 0 | True | False | True | True |
| missing module | 0 | 0 | True | False | False | False |
| stdin leftover | 1 | 1 | True | True | False | True |

Python one-liner, no `inspect` import, labeled rows only:

```bash
python3 -c '
import sys
mod, ver = sys.argv[2], sys.argv[3]
rec, ext = [], []
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if not line or line.startswith("#") or "\t" not in line: continue
    parts = line.split("\t")
    if len(parts) < 3: continue
    r, m, v = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if r == "record": rec.append((m, v))
    elif r == "extension": ext.append((m, v))
key = (mod, ver)
print("in_record", key in rec)
print("in_extension", key in ext)
print("leftover", (key in ext) and (key not in rec))
' "$FIX/084-leftover.rec" golang.org/x/bad v1.0.0
```

```text
in_record False
in_extension True
leftover True
```

Same membership function vs the CLI `leftover_identity` row and rc: **29/29 match**, including swap, hash-changed, no-hash, extra columns, same module@version different hashes, extension-only, record-only, both-same, comments-only, empty, prefix module, prefix version, case, `/go.mod` query, unicode, huge leftover, huge both, trailing tab, whitespace-stripped tokens.

awk of the three load-bearing columns, without hashes:

```awk
BEGIN{FS="\t"}
/^#/ {next}
NF<3 {next}
{
  r=$1; m=$2; v=$3
  gsub(/^[ \t]+|[ \t]+$/, "", r)
  gsub(/^[ \t]+|[ \t]+$/, "", m)
  gsub(/^[ \t]+|[ \t]+$/, "", v)
  if(r=="record") a[m SUBSEP v]=1
  if(r=="extension") b[m SUBSEP v]=1
}
END{
  leftover = (!(mod SUBSEP ver in a)) && (mod SUBSEP ver in b)
  printf "in_record\t%s\n", (mod SUBSEP ver in a)?"yes":"no"
  printf "in_extension\t%s\n", (mod SUBSEP ver in b)?"yes":"no"
  printf "leftover_identity\t%s\n", leftover?"yes":"no"
}
```

owned leftover / good / honest / unseen / missing / swap / hash-changed / no-hash / extra cols / same-mv-diff-hash / extension-only / record-only / both-same / comments / empty / prefix / huge: `awk_eq_cli_loadbearing=True`. Hash column is not in the awk. It does not vote. Naive awk misses CRLF (version field keeps `\r`); the CLI `strip()`s. That is not a tlog.

Nearest ordinary workflow, host-executed:

```bash
grep -n golang.org/x/bad "$FIX/084-leftover.rec"
grep -n golang.org/x/good "$FIX/084-leftover.rec"
```

```text
3:extension	golang.org/x/bad	v1.0.0	h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
2:record	golang.org/x/good	v1.0.0	h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=
```

`demo.sh` says “grep golang.org/x/bad hits the extension line in a raw lookup body”. The fixtures already rewrote the authenticated record as a `record` row and the leftover as an `extension` row. grep of the path hits the leftover because the caller wrote the path on the extension line. leftover is whether they also wrote `record` for that `(module, version)`.

Constitution: a THIN_WRAPPER does not gain extra TSV columns (`h1:`) to escape classification. Those bytes are parsed then dropped. leftover does not read them.

### 2. Swapped regions

Host-executed, leftover file with `record`/`extension` labels swapped, `--module golang.org/x/bad --version v1.0.0`:

```text
module	golang.org/x/bad
version	v1.0.0
in_record	yes
in_extension	no
leftover_identity	no
rc=0
```

`--module golang.org/x/good` on the swapped file: leftover yes, rc=1, replica `stdout_eq=True`. Directional membership, not “unauthenticated extension vs authenticated record.” The harvest leftover is Case B (bad only in the tree-note). After the caller types the labels, leftover is “B has the pair, A does not.” Swap the labels, leftover follows the labels.

### 3. Hashes unused

Owned leftover with the extension `h1:` replaced by `h1:EXTONLY`: leftover yes, rc=1, same five TSV rows. Record hash replaced by `h1:RECONLY`: leftover still yes. No hash column at all (`record MODULE VERSION` / `extension MODULE VERSION`): leftover yes, rc=1. Extra columns after hash: leftover yes.

Same module@version in both regions with **different** hashes:

```text
record	example.com/m	v0.1.0	h1:aaa
extension	example.com/m	v0.1.0	h1:bbb
```

```text
in_record	yes
in_extension	yes
leftover_identity	no
rc=0
```

Unseen both (identical hashes) is the same leftover bit (`no`, rc=0). The unauthenticated hash would still be a leftover hash in the origin lookup body. This CLI does not name it. Identity is the `(module, version)` tuple the caller already labeled. `--version` equal to the owned `h1:` string: leftover no, rc=0 (the hash is not a version token).

### 4. Prefix module

`--module golang.org/x --version v1.0.0` on owned leftover: leftover no, both regions no, rc=0. Same for `golang.org/x/ba`, `golang.org/x/badness`, `golang.org/x/bad/`, `--version v1`, `--version v1.0`, `--version v1.0.0/go.mod`, `V1.0.0`, `Golang.org/x/bad`, trailing space on the module. Exact tuple match. The harvest prefix scan is `path + " " + vers + " "` over a cache payload. This CLI never sees that string. The caller already split it.

Honest `--version v1.3.0/go.mod`: `in_record	yes`, leftover no — that row is a second labeled identity, not a suffix walk.

### 5. Stdin

Owned leftover body on the pipe (`payload` is `-`): leftover TSV, rc=1, replica `stdout_eq=True`. Good module on that pipe: leftover no, rc=0. Empty stdin / `-` with no pipe: leftover no, both regions no, rc=0 (empty payload). `/dev/stdin` leftover: same leftover yes, rc=1.

Unlike peerleft, `-` is stdin. Fine as a one-file tool. The bit is still membership of two caller-labeled lists.

Argv-less / missing `--module` / missing `--version` / extra positional: argparse rc=2, pipe ignored.

### 6. Missing file; empty first region; origin bytes refuse

Missing path: `sumext: [Errno 2] No such file or directory: '/no/such.rec'`, rc=1, no TSV. Directory: `Is a directory`, rc=1. Invalid UTF-8: codec error, no filename in the useful sense, rc=1. BOM: `unknown region '\ufeffrecord'`, rc=1. Embedded NUL: `unknown region '\x00extension'`, rc=1. `tree	…`: `unknown region 'tree'`. `Record	…`: `unknown region 'Record'`.

Empty file and `/dev/null`: leftover no, both regions no, rc=0. Extension-only (`extension	golang.org/x/bad	v1.0.0`, no record rows): leftover yes, `in_record	no`, rc=1. The authenticated record can be empty and leftover still harvests. Record-only (good, no extension): leftover no. Comments-only: leftover no.

Specimen `leftover_lookup_split.txt` as payload: `sumext: …:1: expected region<TAB>module<TAB>version`, rc=1. Space-separated go.sum lines, a FormatRecord-ish lookup body, JSON `{"record":…,"extension":…}`: same parse error, rc=1.

The harvest presence test is a prefix scan of the cache payload after `ParseRecord` authenticates `text` and `ParseTree` ignores extra tree-note lines. Host-executed, those origin bytes are not TSV. leftover no (no TSV). The caller must already have split the lookup body into `record` vs `extension` rows. That split is the product. The CLI reprints it.

### 7. Extra tabs; illegal NAME; query is not validated

`parse_payload` takes `parts[0:3]` as region/module/version. Extra columns after version are dropped. The leftover bit still fires.

An extra tab **before** the module makes the module the empty string: `not a legal NAME`, rc=1, no TSV. Empty version field: same. `module` or `version` equal to `-` on a payload row: `not a legal NAME`. Two fields only / spaces instead of tabs: `expected region<TAB>module<TAB>version`.

`--module` / `--version` are not legal-NAME checked. Empty `--module`, `--module -`, `--version -`, `--module` with an embedded tab: leftover no, rc=0, TSV printed (`name` row may grow a third field). Query `-` cannot match a payload row because the parser forbids `-` as a NAME. Duplicate extension rows: leftover yes (`in` on a list).

Whitespace around tokens is stripped: `  extension  \t  golang.org/x/bad  \t  v1.0.0  ` leftover yes.

### 8. Huge dump; still membership

10000 `record	example.com/pkgN	v1.0.0` rows plus `extension	golang.org/x/bad	v1.0.0`: leftover yes, rc=1, stdout **91** bytes, 0.032s. Same 10000 plus the identity on both regions: leftover no, rc=0, 91 bytes, 0.029s. No cap. No names dumped. The useful bit is still `(module, version) in extension and not in record`.

Tests never hit duplicates, origin, extra tabs, swapped labels, hash change, prefix, same-identity different hashes, or empty first region. They do hit stdin and missing file. Happy path is real. That is not enough.

---

## Primitive

Reality-stripped operation: parse one TSV file of `record|extension MODULE VERSION [ignored hash]`; leftover iff `--module --version` is in the extension list and not the record list; print five TSV rows; rc=1 iff that bit.

Nearest ordinary workflow: `awk '$1=="extension"'` vs `awk '$1=="record"'` on two caller-labeled columns, or `python3 -c 'print((mod,ver) in ext and (mod,ver) not in rec)'` on the pairs the caller already labeled, or `grep '^extension'` / `grep '^record'`. Observable capability lost if sumext vanishes: **none**. The excerpt already is the input. The leftover-vs-record join is still a hand comparison after the caller typed `extension` vs `record`. grep of the path hits the leftover because the fixture contains the path on the extension line.

That is why this is KILL, not MUTATE. The *question* (after `Client.Lookup` of a module whose only matching go.sum line sits in the signed tree-head extension, is that identity leftover unauthenticated text, or present in the authenticated record — grep hits the extension line) is a real debugging object. This embodiment does not ask it of a lookup body. It asks `(module, version) in extension and not in record` on caller-labeled tokens. Adding a `tlog.ParseRecord` / `ParseTree` walk, or ingesting a lookup HTTP body, would be implementing the go theater the harvest rejected, and would be a new harvest, not a patch of this 97-line `in`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Honor-KILLed peerleft is the same leftover = in B not in A on two caller-labeled regions.

Hardcoded ceiling:

- leftover iff extension membership and not record membership; hashes do not vote
- leftover yes ⇒ in_extension yes and in_record no
- leftover yes with empty record (`/dev/null`, empty file, extension-only)
- both regions / record-only / neither: leftover no, same bit
- same module@version different hashes: leftover no
- swap of labels inverts leftover
- prefix / case / `/go.mod` query / hash-as-version: leftover no unless that exact tuple was labeled
- extra tab after version is dropped; extra tab before the module is `not a legal NAME`
- `-` is stdin; empty stdin is leftover no
- origin lookup body / go.sum lines / JSON / `tree` / `Record` / BOM / NUL refuse
- 10k-row leftover still 91-byte sticker, ~0.03s
- rc=1 on leftover **or** parse/IO; argparse rc=2 on missing argv
- Dreamer Lookup was rejected; this is that leftover, reduced to the harvest sentence as `in`

Honor KILL. Dreamer ancestry is not protection.

Do not grow a tlog parser or a lookup-body prefix scan to escape THIN_WRAPPER. Do not merge this join onto `main`. No go. Do not send go theater back to R1.

---

KILL
