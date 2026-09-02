# DESTROYER keptfp

Date: 2026-09-02 13:30 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/keptfp`

sha256 `758ba31dc4125160d812c1124aa7d63f03c64c1e69a189392ed6448b37e54f01` (4869 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-keptfp-keptfp/keptfp/keptfp` is byte-identical (HEAD `c03e55ac8bab4d208dc6cfabbf46e59e2059a5ba`). Tests 6/6 pass. `demo-1.log` / `demo-2.log` byte-identical.

Origin claim (`CANDIDATE.md`): given a current lockfile hash and cache fingerprint entries, name live vs leftover hashes without deleting the whole cache.

Happy path is real. Specimen-006 owned record: current `f0e1d2c3b4`, one live, two leftover. That is not enough. The implementation is string equality of caller-supplied `lockfile_hash` vs `current`. Size is printed, not summed, not measured. Duplicate entry ids are two rows. Empty tab fields shift columns. Disk is never observed.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/keptfp
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/fixtures
```

No merge onto `main`. No uv. No delete. This object is leftover-vs-live of a hash listing, not a cache cleaner.

---

## What still works

Owned 006 record, unseen mixed members, stdin, `/dev/stdin`, FIFO, process substitution, symlink, filename with a space.

```bash
python3 "$CLI" "$FIX/006-cache.rec"
```

```text
current	f0e1d2c3b4
live	fm_8e9f0a1b	project_a	f0e1d2c3b4	131MB
leftover	fm_7a1b2c3d	project_a	a1b2c3d4e5	124MB
leftover	fm_5c6d7e8f	project_b	a1b2c3d4e5	118MB
live_n	1
leftover_n	2
leftover_members	project_a	project_b
rc=0
```

Prefix hashes (`abc` vs `abcd`) are leftover, not prefix-match. Case (`ABC` vs `abc`) and zero-width space (`k` vs `k\u200b`) are leftover. Current-only record prints `live none` / `leftover none` rc=0. Missing current / unknown field / no TAB / conflicting current / short entry: rc=1. UTF-8 BOM is `unknown field '\ufeffcurrent'` rc=1. Invalid UTF-8 is caught. Member names with spaces and `プロジェクト` survive tab fields. CRLF works. Duplicate `current` with the same hash is silent rc=0; current may appear after entries.

That is the whole useful delta. Attacks below break the leftover-vs-live claim around it, or show the primitive cannot tell a leftover fingerprint from a shifted column.

---

## Implementation

### 1. Identity is hash string-equal, not entry id

Same id, two hashes: both printed. Identity is the hash field.

```bash
printf 'current\tNOW\nentry\tsameid\tproj\tNOW\t10\nentry\tsameid\tproj\tOLD\t20\n' | python3 "$CLI"
```

```text
current	NOW
live	sameid	proj	NOW	10
leftover	sameid	proj	OLD	20
live_n	1
leftover_n	1
leftover_members	proj
rc=0
```

Same id, same hash, twice: `live` twice, `live_n 2`. Duplicate leftover hashes: `leftover_n 2` for one hash. `leftover_members` is unique; `leftover_n` is a row count. A pipe that treats `live_n` as distinct fingerprints overcounts.

### 2. Empty tab fields shift columns

`parse_record` does `parts = [p for p in rest.split("\t") if p]`. Empty fields disappear; later columns slide left.

Empty member (`entry id <empty> hash 10`), current is `hash`:

```bash
printf 'current\thash\nentry\tid\t\thash\t10\n' | python3 "$CLI"
```

```text
current	hash
live	none
leftover	id	hash	10	-
live_n	0
leftover_n	1
leftover_members	hash
rc=0
```

The live hash became the member name. Size became the lockfile hash. The entry that should have been live is leftover. `leftover_members` names the current hash.

Empty hash field (`entry id mem <empty> 10`): leftover `id mem 10 -`. Size became the hash. Current `hash` never matched.

`current<TAB>` is not `empty current`. `raw.strip()` eats the trailing tab, the line becomes `current`, parser demands `key<TAB>value` rc=1.

### 3. Size is a recorded string; a path column is dropped

Owned sizes `131MB` / `124MB` / `118MB` are echoed. They are not parsed, not summed, not compared to disk. Two leftover `124MB`+`118MB` do not become a reclaimable total.

200_000 digit size: rc=0, stdout 200083 bytes. The leftover row dumps the payload. Not a disk measurement.

Fifth field is ignored. Caller can name leftover paths; the CLI will not print them.

```bash
printf 'current\thash\nentry\tid\tmem\told\t10\t/cache/old\nentry\tid2\tmem\thash\t11\t/cache/live\n' | python3 "$CLI"
```

```text
live	id2	mem	hash	11
leftover	id	mem	old	10
```

No `/cache/old`. The harvest question was leftover fingerprints beside live artifacts. The one field that would let a human `rm` a leftover without wiping the cache is discarded.

Empty size then extra (`entry id mem hash <empty> PATH`): empty dropped, `PATH` becomes size, live `id mem hash PATH`. A cache path is reported as size.

Omitted size is `-` (documented). Extra fields after size vanish.

### 4. `current` is rest-stripped; entry hashes are not; extra current columns join the hash

`current` takes `rest.strip()` as the whole hash. Entry hashes are split fields and are not stripped.

```bash
printf 'current\tabc\nentry\te1\tm\tabc \t1\n' | python3 "$CLI"
```

```text
current	abc
live	none
leftover	e1	m	abc 	1
rc=0
```

Trailing space on the entry hash makes a leftover of an otherwise live fingerprint. `current\t abc` would have stripped.

Extra tab on current:

```bash
printf 'current\thash\textra\nentry\tid\tmem\thash\t10\n' | python3 "$CLI"
```

```text
current	hash	extra
live	none
leftover	id	mem	hash	10
```

`current` is `hash\textra`. Every entry whose hash is `hash` is leftover. Duplicate current with a different hash is the one conflict that errors. Extra columns on a single `current` line do not.

NUL in current (`k\x00x` vs entry `k`): leftover rc=0. Opaque string equality is the whole identity theory.

### 5. `none` collides with the empty-list sentinel

Member named `none`, leftover:

```bash
printf 'current\tlive\nentry\te1\tnone\told\t1\n' | python3 "$CLI"
```

```text
live	none
leftover	e1	none	old	1
live_n	0
leftover_n	1
leftover_members	none
rc=0
```

All-live (no leftover members):

```text
leftover	none
leftover_n	0
leftover_members	none
```

`leftover_members	none` means both empty and the member `none`. A pipe that keeps rows where that field is not `none` drops the leftover. Current-only (`live none` / `leftover none` / `leftover_members none`) is the same three tokens as “I looked, nothing is leftover” and as “a leftover member is named none”. Tests split on tab and compare lists, so they cannot see it.

### 6. Disk is never observed; leftover is rc=0; nothing is deleted

CANDIDATE.md: “Does not delete.” Honored. Also: does not `stat`. Dummy dirs `cache/old` and `cache/live` still exist after a leftover report. Declared leftover with no files is leftover. Declared live with no files is live. The `.rec` is the answer’s ingredients.

All leftover, mixed leftover, current-only: rc=0. `ls` of a leftover path is rc=1 from `test -e`. This CLI is rc=0 while printing `leftover_n 2`. Fine as a printer; hostile as a pipe predicate. CANDIDATE suggested naming leftover without a whole-cache wipe. There is no `--check`. 5000 leftover rows: rc=0 in 0.03s, `leftover_n 5000`, ten leftover_members columns.

`#entry ...` is a comment. Comment out the leftover rows of 006 and the report is `leftover none` rc=0. The join is only as honest as the handwritten record.

Honesty on the owned record:

```bash
awk -F'\t' '$1=="current"{c=$2} $1=="entry"{if($4==c) print "live",$2,$3,$4,$5; else print "leftover",$2,$3,$4,$5}' OFS='\t' "$FIX/006-cache.rec"
```

```text
leftover	fm_7a1b2c3d	project_a	a1b2c3d4e5	124MB
live	fm_8e9f0a1b	project_a	f0e1d2c3b4	131MB
leftover	fm_5c6d7e8f	project_b	a1b2c3d4e5	118MB
```

Same partition. keptfp adds `live_n` / `leftover_n` / unique `leftover_members` / `none` sentinels. `demo.sh` already prints the three entries and the current hash before invoking the CLI.

### 7. Parse edges (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory as record | 1 | `Is a directory` |
| empty file / `/dev/null` | 1 | `missing current` |
| invalid UTF-8 | 1 | `'utf-8' codec can't decode` |
| UTF-8 BOM | 1 | `unknown field '\ufeffcurrent'` |
| `Current` (field case) | 1 | `unknown field 'Current'` |
| empty current after strip | 1 | `expected key<TAB>value` (tab stripped) |
| two positional args | 2 | argparse |
| JSON object | 1 | `expected key<TAB>value` |
| `-` as RECORD | 1 | `No such file or directory: '-'` (stdin is the omitted arg) |
| `/dev/stdin`, FIFO, proc subst, symlink | 0 | works |
| comments / blank lines | 0 | skipped |
| CRLF | 0 | `splitlines` |
| NUL in current | 0 | leftover vs `k` |
| 200k digit size | 0 | 200083 byte leftover row |
| 5000 leftovers | 0 | no cap |

These do not save the identity, shift, or observation holes.

---

## Primitive

Reality-stripped operation: parse a TSV of `current HASH` plus `entry ID MEMBER HASH [SIZE]`; `lockfile_hash == current`; print live rows, leftover rows, counts, unique leftover members.

Nearest ordinary workflow: the fixture already names current `f0e1d2c3b4` and three `(id, member, hash, size)` tuples. `awk` of column 4 vs current partitions them. `ls` of fingerprint dirs still leaves that join as a hand comparison — but this CLI does not list dirs. `demo.sh` writes the join into `.rec` files, then the CLI reprints it.

Observable capability lost if keptfp vanishes: the **named join** (live vs leftover plus leftover member names) as one TSV. That join is real when the caller already knows each entry’s lockfile hash and the current hash. It is not a uv/cargo cache reconstruction, not a deleter (research boundary, honored).

That is why this is not KILL: the *question* (this hash is current, those hashes are leftover, do not wipe the whole cache) is a debugging object `rm -rf cache` will not emit. The current embodiment is a specimen-006 record comparator that labels any string-unequal hash leftover.

The ceiling is already written down, and it is too small for the claim:

- leftover = `lockfile_hash != current`, including shifted columns, padded hashes, extra `current` fields, and forgotten files
- identity is hash, not id; duplicate ids are two rows
- size is a recorded string; a path column is dropped; 200k digits dump
- `none` means both empty and the member `none`
- no filesystem observation; dummy leftover dirs survive; declared leftover with no files is leftover
- leftover is always rc=0
- the owned record’s hashes are supplied by the rewrite; the CLI will not discover them from a cache tree

Do not grow a uv fingerprint reconstruction to escape this. Do not merge this join into a blob-hash identity tool. Keep the leftover-vs-live row.

---

## Mutation (what must change)

Keep the object: for a current lockfile hash and cache fingerprint entries, leftover hashes sit beside live artifacts and are named without a whole-cache wipe.

Do not keep a printer that string-equals caller-supplied hashes and calls the difference leftover.

1. **Empty tab fields are errors, not slides.** `entry id <empty> hash` is rc≠0, not leftover member=`hash`. Per-field strip or refuse padded hashes. Extra columns on `current` are an error, not `hash\textra`. If the mutation still shifts columns into leftover, a later destroyer should KILL.

2. **Identity is the fingerprint id (and optional path), not only hash equality.** Duplicate ids with different hashes are a conflict or two named slots (`id` + hash), not two silent rows. `live_n` / `leftover_n` are distinct ids, or the report says `rows`. Same hash on two members stays two members.

3. **Size is measured or unlabeled.** Recorded `131MB` is `declared_size`, not size. Sum only if parsed; unparsable is not a dump. A fifth field is `path` (or refused). 200k digit leftover rows are capped or hashed.

4. **`none` is not a list value.** Empty leftover members is a distinct token (`-`, `.`, or a count column). A member named `none` must not render as the empty sentinel.

5. **Leftover is observed or declared-with-source.** A leftover row with no path and no `--dir` is `declared`, not “this cache entry is leftover on disk”. `--dir` that still contains the leftover path should say so; missing path should say missing. Dummy dirs must not survive a claimed wipe — this tool still must not `rm -rf` the whole cache; it may name paths. Omitting every leftover `entry` (comment) is not `leftover none` of a cache.

6. **rc=1 on leftover_n>0** (or `--check` as the default predicate). rc=0 only for observed all-live / current-only. Cap huge leftover dumps.

7. **Ingest a cache listing or refuse.** Either parse fingerprint-dir names / lockfile-hash suffixes so `demo.sh` is not a handwritten `.rec` that already contains `f0e1d2c3b4`, or drop the implication that the CLI named leftover hashes from a cache. Still do not invent uv `cache clean --type=workspace-member`. Still do not delete.

If the mutation cannot do (1)+(5)+(6), the object is still `awk $4==current` with extra print, and a later destroyer should KILL.

---

MUTATE
