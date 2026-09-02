# DESTROYER vcache

Date: 2026-09-02 15:59 JST
RUN_ID: specimen-hdd-20260902-1112
job: job-0415 (worker destroyer-vcache, CLAIMED)
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-vcache/vcache`

sha256 `04fc6bb1f0b10a6d1b2c011c6e4639409d20ccf298e3a7acba3bd6ed880534d6` (2801 bytes, 95 lines). No `vcache` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-vcache/`) and was not merged. Host Python 3.14.5. `vitest` is **not on PATH**. `npx` and `node` are on PATH (`/opt/homebrew/bin/npx`, `/opt/homebrew/bin/node`) and **were not executed**.

Origin claim (`CANDIDATE.md` / harvest `hdd-vcachekey` / specimen-094 leftover fsModuleCache key minted before `shouldExternalize`): leftover_key = externalize AND cache_key present AND NOT disk_write on caller-labeled `externalize` / `cache_key` / `disk_write` TSV flags. grep of the id hits memory write; the miss is fs empty. Kind: USEFUL_COMPOSITION. Owned packet: Case B ordinary file id, memory key `H_ext` minted, disk file never written. Rejected: invented vitest run transcripts. Constraint: owned labeled identity records. No vitest.

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.083s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 361 bytes). That is not enough.

This candidate is a **THIN_WRAPPER** of three caller flags: `yn_in(externalize) and (cache_key not in {"", "-"}) and not yn_in(disk_write)`. `inspect()` never reads a cache root, never SHA-1s file bytes, never calls `shouldExternalize`, never `ls`es `node_modules/.experimental-vitest-cache`, never looks at `id` when it decides leftover. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on leftover+rc for **34/34** parse-success host cases (`stdout_eq=True`). A python one-liner of those three flags matches leftover+rc on the harvest shapes plus omit-key / hyphen / missing-disk / true-false / 1-0. yn(11) × key(8) × disk(11) token grid: **968/968** replica+thin. awk of the four TSV keys matches the load-bearing leftover columns on **31/34** (extra tab / leading tab / CRLF are the parser's `strip()`, not an fsModuleCache walker). Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-vcache/vcache
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-vcache/fixtures
S094=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-094
```

No merge onto `main`. No vitest. Do not grow a `generateCachePath` / `shouldExternalize` / `.experimental-vitest-cache` walker to escape THIN_WRAPPER. Do not send vitest theater back to R1. First HARVEST is not protection. Same shape as Honor-KILLed pnpbuilt (leftover = flag A and not flag B) plus a presence check on the third caller-typed field. Kill condition `thin three flags` holds.

---

## What still works

Owned leftover, owned inlined, unseen `widget` copies of those two, and any other TSV whose rows are already `externalize yes|true|1` vs a nonempty non-hyphen `cache_key` vs `disk_write` not in that yes-set, **when the question is only whether those three caller-labeled tokens satisfy the harvest sentence**.

```bash
python3 "$CLI" "$FIX/094-ext.rec"
echo rc=$?
```

```text
id	lodash-es
externalize	yes
cache_key	H_ext
disk_write	no
leftover_key	yes
rc=1
```

76 bytes. Stderr empty. Byte-identical to `printf` of those five TSV rows. Owned inlined: `id	./sum.js` / `externalize	no` / `cache_key	H_inlined` / `disk_write	yes` / leftover no, rc=0, 78 bytes, also `printf`-identical. Unseen `widget` leftover: same five rows with that id and `H_w`, leftover yes, rc=1.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode id `依存1` / key `鍵0`: leftover yes, rc=1. 10000 comment lines plus leftover flags: leftover yes, rc=1, stdout **68** bytes (id `x`), ~0.027s. Same 10000 plus inlined flags: leftover no, rc=0, 71 bytes, ~0.026s. Missing path / directory / invalid UTF-8 / BOM / binary NUL / unknown field / origin split / JSON / TypeScript: `vcache: …` rc=1. No args / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `ext and key present and not disk` already does on three caller-labeled fields.

---

## Implementation

`inspect()` in full:

```python
def inspect(fields: dict[str, str]) -> dict:
    ext = yn_in(fields.get("externalize") or "")
    key = fields.get("cache_key") or "-"
    disk = yn_in(fields.get("disk_write") or "")
    leftover = ext and key not in {"", "-"} and not disk
    return {
        "id": fields["id"],
        "externalize": ext,
        "cache_key": key,
        "disk_write": disk,
        "leftover_key": leftover,
    }
```

`inspect.co_names` is `('yn_in', 'get')`. `inspect.co_varnames` is `('fields', 'ext', 'key', 'disk', 'leftover')`. `inspect.co_consts` includes `'externalize'`, `'cache_key'`, `'-'`, `'disk_write'`, `'id'`, `'leftover_key'`, `frozenset({'', '-'})`. dis: two `yn_in` calls (`externalize`, `disk_write`), `fields.get("cache_key") or "-"`, then `ext` AND `key not in {"", "-"}` AND `UNARY_NOT` of `disk`. There is no prefix, no sha1, no file content, no `shouldExternalize`, no cache root, no `[empty]` log, no vitest.

`yn_in` is `val in {"yes", "true", "1"}`. `parse_record` accepts keys `id` / `externalize` / `cache_key` / `disk_write` only. First tab splits key/value; `rest.strip()` is the value. Unknown keys raise. `id` is required and echoed. leftover never reads `id` except to reprint it. `externalize` / `disk_write` print as `yn()` of membership, not the raw token. `cache_key` prints raw (or `-`).

When leftover is yes, `externalize` is always yes and `disk_write` is always no and `cache_key` is never `-`. Tests never hit omitted key, hyphen, missing disk, extra tabs, origin bytes, stdin, `true`/`1`, `present`, `YES`, or the token grid. Three tests: owned leftover, owned inlined, missing file.

`demo.sh` already names the nearest operation: `leftover is a minted key with externalize yes and disk_write no`.

---

## Attacks

### 1. THIN_WRAPPER of `ext and key present and not disk`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on the harvest shapes:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | ext | key | disk |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| owned leftover (B) | 1 | 1 | True | True | True | H_ext | False |
| owned inlined (A) | 0 | 0 | True | False | False | H_inlined | True |
| unseen widget leftover | 1 | 1 | True | True | True | H_w | False |
| unseen widget inlined | 0 | 0 | True | False | False | H_w | True |
| stdin leftover | 1 | 1 | True | True | True | H_ext | False |

Python one-liner, no `inspect` import, labeled flags only:

```bash
python3 -c '
import sys
YES={"yes","true","1"}
fields={}
for raw in open(sys.argv[1], encoding="utf-8"):
    line=raw.strip()
    if not line or line.startswith("#") or "\t" not in line: continue
    k,r=line.split("\t",1)
    fields[k.strip()]=r.strip()
ext=fields.get("externalize","") in YES
key=fields.get("cache_key") or "-"
disk=fields.get("disk_write","") in YES
print("externalize", ext)
print("cache_key", key)
print("disk_write", disk)
print("leftover", ext and key not in {"", "-"} and not disk)
' "$FIX/094-ext.rec"
```

```text
externalize True
cache_key H_ext
disk_write False
leftover True
```

Same three-flag function vs the CLI leftover row and rc: owned leftover / inlined / unseen / omit-key / hyphen / missing-disk / true-false / 1-0 / present / YES all match. yn-ish × key × disk token grid: **968/968**. Empty-field triples are `expected key<TAB>value` because `line.strip()` eats a trailing tab (`cache_key\t` becomes `cache_key`). That is not an fsModuleCache walker.

awk of the four load-bearing columns, without treating `id` as a vote:

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
  ext = (f["externalize"]=="yes" || f["externalize"]=="true" || f["externalize"]=="1")
  key = f["cache_key"]; if (key == "") key = "-"
  disk = (f["disk_write"]=="yes" || f["disk_write"]=="true" || f["disk_write"]=="1")
  leftover = ext && (key != "") && (key != "-") && !disk
  printf "externalize\t%s\n", ext?"yes":"no"
  printf "cache_key\t%s\n", (f["cache_key"]==""?"-":f["cache_key"])
  printf "disk_write\t%s\n", disk?"yes":"no"
  printf "leftover_key\t%s\n", leftover?"yes":"no"
}
```

owned leftover / inlined / unseen / true-false / 1-0 / omit-key / hyphen / missing-disk / missing-ext / id-only / unicode / huge / duplicates: `awk_eq_cli_loadbearing=True`. 31/34 overall. `id` is not in the leftover bits. Naive awk misses extra-tab (CLI keeps `yes\textra`, which is not in the yes-set), leading tab (CLI `strip()`s it into `yes`; awk `$2` is empty), and CRLF (awk version field keeps `\r`). That is not a cache directory.

Nearest ordinary workflow, host-executed:

```bash
grep -n lodash-es "$FIX/094-ext.rec"; echo leftover_id_rc=$?
grep -n H_ext "$FIX/094-ext.rec"
grep -n lodash-es "$FIX/094-inline.rec"; echo inline_id_rc=$?
ls "$FIX"/**/.experimental-vitest-cache
ls "$FIX"/**/H_ext
```

```text
2:id	lodash-es
leftover_id_rc=0
4:cache_key	H_ext
inline_id_rc=1
ls cache in fixtures []
ls H_ext []
```

`demo.sh` says “grep memory write vs fs empty”. grep of `lodash-es` hits leftover because the caller wrote that token as `id`. grep of `H_ext` hits leftover because the caller wrote it as `cache_key`. There is no cache root and no disk file in the fixtures. leftover is whether they also wrote `externalize	yes` and `disk_write	no` and a nonempty non-hyphen `cache_key`.

Shell of the owned leftover triple:

```bash
# leftover yes; rc=1
test "$ext" = yes && test -n "$key" && test "$key" != - && test "$disk" != yes
```

Owned inlined (`ext` no, `disk` yes, key `H_inlined`): leftover no, rc=0.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`id`, reprinted `externalize` / `cache_key` / `disk_write`) to escape classification. Those rows are the inputs. leftover does not hash them.

### 2. leftover only on the harvest triple; 2×2×2

Host-executed yes/no × key present/`-` × disk yes/no:

| ext | disk | key | leftover_key | rc |
| --- | --- | --- | --- | ---: |
| yes | yes | H_ext | no | 0 |
| yes | yes | - | no | 0 |
| yes | no | H_ext | yes | 1 |
| yes | no | - | no | 0 |
| no | yes | H_ext | no | 0 |
| no | yes | - | no | 0 |
| no | no | H_ext | no | 0 |
| no | no | - | no | 0 |

Leftover fires in **one** cell: externalize yes-set, cache_key present, disk_write not yes-set. That is the harvest sentence. The other seven cells are leftover no, rc=0. `id` never changes leftover.

ext yes / key present / disk yes (inlined-shaped with leftover ext): leftover no, rc=0. ext no / key present / disk no: leftover no, rc=0. Both flags yes or both no: leftover no.

### 3. `cache_key` is presence, not a hash and not `yn_in`

Harvest leftover is a leftover SHA-1 path `join(cacheRoot, H_ext)`. Host-executed against `cache_key	sha1-deadbeef` / `externalize	yes` / `disk_write	no`: leftover yes, rc=1. The hash bytes are the **value** token. They are present (`not in {"", "-"}`). leftover yes. Same leftover yes for `cache_key	yes`, `cache_key	no`, `cache_key	0`. Presence is not a boolean. `no` as a key still leftover-harvests.

Omit `cache_key` with leftover flags:

```text
id	x
externalize	yes
cache_key	-
disk_write	no
leftover_key	no
rc=0
```

`key` printed `-` is `fields.get("cache_key") or "-"`. leftover uses that `-`, so leftover no. Hyphen collision: caller types `cache_key	-` — same five rows, leftover no, rc=0. Format’s missing-key sticker `-` is also the “not present” token.

Case C (data: / `@vite/client` / network — `{externalize}` before `getCachePath`, no `H_key`): `externalize	yes` / `cache_key	-` / `disk_write	no` → leftover no, rc=0. Case D bail / Case E cache off: leftover no because ext is no and/or key is `-`. The CLI cannot tell omitted-before-mint from hyphen-as-name. The caller must already have reduced a memory-vs-disk observation to `cache_key	H_ext` vs `-`. That reduction is the product. The CLI reprints it.

`present` as `externalize` is **not** in `{yes, true, 1}`: leftover no, `externalize	no`, rc=0. `YES` / `Yes` / `on` / `hash`: leftover no. `true` / `1` vs a non-yes disk: leftover yes, rc=1. Unlike Honor-KILLed pnpbuilt, `present` is not in this yes-set.

### 4. `id` is a spectator; missing disk still leftover

Host-executed, leftover flags plus any id (`lodash-es`, `widget`, `依存1`, `data:text/js` with a present key): leftover follows the three flags, not the id. Duplicate `id` last-wins and still does not vote.

`id	x` / `externalize	yes` / `cache_key	H_ext` and no `disk_write` row:

```text
id	x
externalize	yes
cache_key	H_ext
disk_write	no
leftover_key	yes
rc=1
```

The disk side can be omitted and leftover still harvests (`yn_in("")` is false, so `not disk` is true). `/dev/null` is not a valid record (`need id`). Id-only: leftover no, `externalize	no` / `cache_key	-` / `disk_write	no`, rc=0.

`id	x` / `cache_key	H_ext` / `disk_write	no` and no `externalize`: leftover no, rc=0. Duplicate `externalize` last-wins (`yes` then `no` → leftover no; `no` then `yes` → leftover yes). Duplicate `disk_write` last-wins (`no` then `yes` → leftover no).

### 5. Extra tabs; empty field; stdin

`parse_record` takes `rest.strip()` after the first tab. Extra columns after `yes` stay in the value: `externalize	yes	extra` → token `yes\textra` → not in the yes-set → leftover no, rc=0. Replica `stdout_eq=True`. awk `$2` is `yes` and disagrees. The leftover bit still follows `yn_in`. `id` reprints as `x	extra`.

An extra tab **before** the value (`externalize\t\tyes`): `strip()` eats the leading tab; token is `yes`; leftover yes, rc=1.

Extra tab after a present key (`cache_key	H_ext	extra`): token `H_ext\textra` is still present; leftover yes, rc=1; `cache_key` reprints with the extra column.

Extra tab after a would-be disk write (`disk_write	yes	extra`) on leftover-shaped ext+key:

```text
id	x
externalize	yes
cache_key	H_ext
disk_write	no
leftover_key	yes
rc=1
```

The caller typed `yes	extra`. Membership misses. `format_report` prints `disk_write	no` (`yn(False)`). leftover harvests a “disk write” the caller labeled yes. That is not an fs empty check. It is `yn_in`.

Empty value (`cache_key\t\n`): `line.strip()` eats the trailing tab; `expected key<TAB>value`, rc=1, no TSV. Same for empty `externalize	` / `disk_write	`. Spaces instead of a tab: `expected key<TAB>value`, rc=1.

`-` is stdin. Owned leftover body on the pipe: leftover TSV, rc=1, replica `stdout_eq=True`, byte-identical to the file path. Empty stdin: `vcache: <stdin>: need id`, rc=1. `/dev/stdin` leftover: leftover yes, rc=1. Process substitution `<(cat 094-ext.rec)`: leftover yes, rc=1. Fine as a one-file tool. The bit is still three caller-labeled flags.

Argv-less / extra positional: argparse rc=2, pipe ignored.

### 6. Origin bytes refuse; vitest artifacts are not parsed

Specimen `leftover_identity_split.txt` as record: `expected key<TAB>value`, rc=1. `fetch_order_failing.ts` / `generate_cache_path_failing.ts` / `early_externalize_omit.ts`: same parse error, rc=1. JSON `{"id":"lodash-es","externalize":"yes",…}`: same. `contenthash	abc`: `unknown field 'contenthash'`, rc=1. `Id	x`: `unknown field 'Id'`, rc=1. Comments-only: `need id`, rc=1. UTF-8 BOM: `unknown field '\ufeffid'`, rc=1. Embedded NUL: `unknown field '\x00externalize'`, rc=1. Invalid UTF-8: codec error, no leftover TSV, rc=1.

The harvest presence test is “grep of the id in the memory-write log plus ls of `join(cacheRoot, H_ext)`.” Host-executed, those origin bytes are not TSV. leftover no (no TSV). The caller must already have split Case B into `externalize	yes` / `cache_key	H_ext` / `disk_write	no`. That split is the product. The CLI reprints it.

### 7. Huge dump; still three flags

10000 `# pad` lines plus leftover flags: leftover yes, rc=1, stdout **68** bytes, 0.027s. Same 10000 plus inlined flags: leftover no, rc=0, 71 bytes, 0.026s. No cap. No cache keys dumped. The useful bit is still `ext and key present and not disk`.

Missing path: `No such file or directory`, rc=1. Directory: `Is a directory`, rc=1. Tests never hit duplicates, origin, extra tabs, stdin, omitted key, hyphen, missing disk, `present`, `YES`, or the token grid. They do hit missing file. Happy path is real. That is not enough.

---

## Primitive

Reality-stripped operation: parse one TSV file of `id` plus optional `externalize` / `cache_key` / `disk_write`; leftover iff `externalize` is in `{yes,true,1}` and `cache_key` is nonempty and not `-` and `disk_write` is not in that yes-set; print five TSV rows; rc=1 iff leftover. `id` is a spectator string. Missing `cache_key` prints as `-` and does not vote. Missing `disk_write` votes as not-yes and still leftover-harvests.

Nearest ordinary workflow: `grep '^externalize'` vs `grep '^cache_key'` vs `grep '^disk_write'` on the flags the caller already labeled, or `python3 -c 'print(ext and key not in {"","-"} and not disk)'`, or the awk above. Observable capability lost if vcache vanishes: **none**. The excerpt already is the input. The leftover-vs-inlined join is still a hand comparison after the caller typed `externalize	yes` vs `disk_write	no` vs `cache_key	H_ext`. grep of the id hits leftover because the leftover fixture contains `lodash-es`. `ls` of `.experimental-vitest-cache` / `H_ext` finds nothing in the fixtures.

That is why this is KILL, not MUTATE. The *question* (after `shouldExternalize` returns true for an ordinary file id, does memory still name leftover already-hashed `H_ext` while the disk file is absent, or omitted the way Case C / E never minted a key — grep hits the id, the miss is fs empty) is a real debugging object. This embodiment does not ask it of vitest, `generateCachePath`, or a cache directory. It asks `ext and key present and not disk` on caller-labeled tokens. Adding a vitest `DEBUG=vitest:cache:fs` runner, a `saveMemoryCache` / `getCachedModule` walk, or ingesting `node_modules/.experimental-vitest-cache`, would be implementing the vitest theater the harvest rejected, and would be a new harvest, not a patch of this 95-line `and not`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Honor-KILLed pnpbuilt is leftover = flag A and not flag B on two caller-labeled flags. Honor-KILLed cssleft is leftover = two string comparisons on caller-typed names. Honor-KILLed fingerid is leftover = three string equalities. This is leftover = three caller flags (two yes-sets plus presence).

Hardcoded ceiling:

- leftover iff ext yes-set and cache_key present and disk not yes-set; id does not vote
- leftover yes ⇒ externalize yes and disk_write no and cache_key not `-`
- leftover yes with missing disk (`externalize	yes` / `cache_key	H_ext` only)
- omitted cache_key / `cache_key	-` / Case C omitted: leftover no even with ext yes and disk no
- both yes / both no / ext no: leftover no, same bit
- `cache_key	yes` / `no` / `0` / `sha1-deadbeef` are present (not yn_in)
- `yes` / `true` / `1` are one yes-set; `present` / `YES` / `on` are not
- extra tab after the value stays in the token and misses the yes-set; extra tab before the value is `strip()`ped
- `disk_write	yes	extra` reprints `disk_write	no` and leftover-harvests
- empty field after strip is `expected key<TAB>value`
- `-` is stdin; empty stdin is `need id`
- origin split / TS / JSON / `contenthash` / `Id` / BOM / NUL refuse
- 10k-comment leftover still 68-byte sticker, ~0.027s
- rc=1 on leftover **or** parse/IO; argparse rc=2 on missing argv
- Dreamer vitest run was rejected; this is that leftover, reduced to the harvest sentence as `and` / `not in` / `and not`

Honor KILL. Dreamer ancestry is not protection.

Do not grow a vitest runner, a `generateCachePath` hasher, or an `.experimental-vitest-cache` walker to escape THIN_WRAPPER. Do not merge this join onto `main`. No vitest. Do not send vitest theater back to R1.

---

KILL
