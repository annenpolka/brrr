# DESTROYER keptfp 2

Date: 2026-09-02 15:46 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0385
Worker: destroyer-keptfp-2

Target (archive; mutate never queued):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/keptfp`

sha256 `758ba31dc4125160d812c1124aa7d63f03c64c1e69a189392ed6448b37e54f01` (4869 bytes, 156 lines). Same digest as `DESTROYER_keptfp.md`. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-keptfp-keptfp/keptfp/keptfp` is byte-identical (`cmp` rc=0). HEAD `c03e55ac8bab4d208dc6cfabbf46e59e2059a5ba` (`Record keptfp empirical transcript from demos.`), branch `specimen-hdd/candidate-keptfp-keptfp`. Parent `main` is `432f954c0dce09f1b72084a66075051d884cba61`; `git ls-tree HEAD keptfp` empty. Host Python 3.14.5. unittest 6/6 (`Ran 6 tests in 0.104s` `OK`). `demo-1.log` / `demo-2.log` byte-identical. `uv` is on PATH and was not invoked. Not merged onto `main`. Archive was not edited. No `MUTATE.md`. No `mutate-keptfp` job in `jobs.jsonl`.

Origin (`CANDIDATE.md` / harvest `hdd-uvcache` / specimen-006): given a current lockfile hash and cache fingerprint entries, name live vs leftover hashes without deleting the whole cache. Kind: USEFUL_COMPOSITION. Embodiment: TSV `current` plus `entry` rows. uv is not executed.

First destroyer (`DESTROYER_keptfp.md`) **MUTATE**: identity is hash string-equal; empty tabs slide; size is a recorded string; path column dropped; `none` collides with the empty sentinel; disk is never observed; leftover is always rc=0. Kill condition for a later destroyer: if mutation cannot do empty-tab-as-error (1) + leftover observed-or-declared-with-source (5) + rc=1 on leftover_n>0 (6), the object is still `awk $4==current` with extra print, **KILL**. First MUTATE is not protection.

This candidate is a **THIN_WRAPPER of caller fingerprint membership**: `lockfile_hash == current` live, `!=` leftover, on a table the caller already labeled. Independent replica (does not import keptfp; `destroyers/_keptfp2_scratch/replica.py`) is **byte-identical** to CLI stdout+rc on 35/35 success cases and stdout+stderr+rc on 10/10 stdin error cases. awk of column 4 vs `current` matches the CLI live/leftover partition on the owned 006 record. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/keptfp
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-keptfp/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-keptfp-keptfp/keptfp/keptfp
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run uv. Do not merge with freshmiss / lockident. Do not grow a cargo/uv fingerprint-dir walker to escape THIN_WRAPPER. Do not send leftover-hash theater back to R1.

---

## What still works

Owned 006 and any other case where the caller already typed `current HASH` and `entry ID MEMBER HASH [SIZE]`.

```bash
python3 "$CLI" "$FIX/006-cache.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-cache.rec"; echo rc=$?
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

```text
current	livehash
live	now_x	crate_x	livehash	11
live	now_y	crate_y	livehash	22
leftover	old_a	crate_x	stale	10
leftover	old_b	crate_y	stale	20
leftover	orphan	crate_z	other	3
live_n	2
leftover_n	3
leftover_members	crate_x	crate_y	crate_z
rc=0
```

All-live: `leftover none` / `leftover_n 0` / `leftover_members none`, rc=0. Current-only: `live none` / `leftover none`, rc=0. Stdin, `/dev/stdin`, FIFO, process substitution, symlink, filename with a space, CRLF: owned harvest. Missing current / unknown field / no TAB / conflicting current / short entry / UTF-8 BOM / invalid UTF-8 / empty file / `/dev/null` / directory / missing path: rc=1. Two positional args: argparse rc=2. `-` is a missing path, not stdin. unittest 6/6.

That is the first MUTATE surface. It is also `awk` of the hash column against the current token the caller already wrote. Leftover does not change rc.

---

## Implementation

Load-bearing body of `inspect()`:

```python
live = [e for e in entries if e.lockfile_hash == current]
leftover = [e for e in entries if e.lockfile_hash != current]
leftover_members = unique([e.member for e in leftover])
```

`inspect.co_names` is `('lockfile_hash', 'unique', 'member', 'len')`. `format_report.co_names` is `('append', '_fmt_entry', 'join')`. `parse_record` drops empty tab fields (`parts = [p for p in rest.split("\t") if p]`). `main` returns 0 after a successful parse. Source contains no `stat`, `exists`, `is_file`, `unlink`, `uv`, or `cargo`. `Path` is only `read_text`. There is no cache tree.

`demo.sh` already prints the current hash and the three `(id, member, hash)` tuples before invoking the CLI. The `.rec` files already contain the answer as labeled rows.

---

## 1. THIN_WRAPPER of caller fingerprint membership

Replica of leftover+rc (membership; no import):

```python
live = [e for e in entries if e[2] == current]
leftover = [e for e in entries if e[2] != current]
leftover_members = unique([e[1] for e in leftover])
# print live rows, leftover rows, live_n, leftover_n, leftover_members; rc = 0
```

35/35 host success cases: stdout byte-identical, rc identical (owned 006, unseen, all-live, current-only, all-leftover, duplicate id two hashes, duplicate id same hash, duplicate leftover hash, prefix hash, case, zero-width space, trailing-space entry hash, extra current column, empty-member slide, empty-hash slide, empty-size path-as-size, path-dropped, member `none` leftover/live, member space, プロジェクト, CRLF, comment-skip leftover, blank lines, duplicate current same hash, current after entries, NUL in current, omitted size, same hash two members, café, hyphen size, live+leftover same member, fifth field ignored, space in filename, symlink).

10/10 stdin error cases: stdout+stderr+rc byte-identical (JSON object, `Current`, no TAB, empty current after strip, missing current, short entry, conflicting current, UTF-8 BOM, comment-only, empty file).

awk leftover (`$4==current` vs not) equals the CLI live/leftover rows on owned 006 (`fm_8e9f0a1b` live; `fm_7a1b2c3d` / `fm_5c6d7e8f` leftover). File order vs live-then-leftover is formatting. Counts and unique leftover members are `len` / first-seen unique of that partition.

Nearest ordinary workflow: the replica above, or:

```bash
awk -F'\t' '$1=="current"{c=$2} $1=="entry"{if($4==c) print "live",$2,$3,$4,$5; else print "leftover",$2,$3,$4,$5}' OFS='\t' "$FIX/006-cache.rec"
```

`ls` of fingerprint dirs still leaves that join as a hand comparison — but this CLI does not list dirs. The harvest question (this hash is current, those hashes are leftover, do not wipe the whole cache) is real. This embodiment asks it of labeled rows that already are those hashes.

---

## 2. MUTATE leftovers (1)+(5)+(6) still hold; mutation never landed

First-destroyer must-change (1): empty tab fields are errors, not slides. Still slides.

```bash
printf 'current\thash\nentry\tid\t\thash\t10\n' | python3 "$CLI"; echo rc=$?
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

The live hash became the member name. Size became the lockfile hash. Extra columns on `current` still join the hash (`current	hash	extra`); every entry whose hash is `hash` is leftover. Empty size then extra path: `PATH` becomes size; a cache path is reported as size.

First-destroyer must-change (5): leftover is observed or declared-with-source. Still neither. Dummy dirs `cache/old` and `cache/live` still exist after a leftover report. The path column is still dropped. Declared leftover with no files is leftover, rc=0. Comment out the leftover rows of 006: `leftover none` rc=0. The join is only as honest as the handwritten record.

First-destroyer must-change (6): rc=1 on leftover_n>0 (or `--check`). Still rc=0. Owned leftover_n 2, all-leftover, mixed, 5000 leftover rows (137874 byte stdout, 0.03s-class): rc=0. There is no `--check`. rc=1 is parse/IO.

Must-change (2) identity-is-id, (3) size-measured-or-unlabeled, (4) `none` not a list value, (7) ingest a cache listing: also unapplied. Duplicate ids with different hashes are still two silent rows. Recorded `131MB` is still echoed. 200000 digit size: rc=0, stdout 200080 bytes. Member named `none` leftover and empty leftover members both print `leftover_members	none`.

Bytes unchanged. No mutate job. Kill condition `still awk $4==current` holds.

---

## 3. `none` is the empty token and a legal member; leftover is not a predicate

```bash
printf 'current\tlive\nentry\te1\tnone\told\t1\n' | python3 "$CLI"
# leftover_members	none     # name none was leftover

printf 'current\tabc\nentry\te1\tm\tabc\t1\n' | python3 "$CLI"
# leftover_members	none     # empty leftover
```

`grep '^leftover_members	none$'` matches both. Current-only is the same three tokens (`live none` / `leftover none` / `leftover_members none`) as “I looked, nothing is leftover” and as “a leftover member is named none”. Tests split on tab and compare lists, so they cannot see it.

`leftover_n` is a row count, not distinct fingerprints. Same id, two hashes: `live_n 1` / `leftover_n 1`. Same id, same hash twice: `live` twice, `live_n 2`. Duplicate leftover hashes: `leftover_n 2` for one hash. `leftover_members` is unique; a pipe that treats `live_n` as distinct fingerprints overcounts.

---

## Primitive

Reality-stripped operation: parse a caller-complete TSV of `current HASH` plus `entry ID MEMBER HASH [SIZE]`; partition by `lockfile_hash == current`; print live rows, leftover rows, counts, unique leftover members; exit 0 if the table parsed.

Nearest: the replica in §1, or awk of that membership test. Observable capability lost if keptfp vanishes: **none**. The named join the first destroyer kept is formatting of caller fingerprint membership (`live_n` / `leftover_n` / unique members / `none` sentinels). `demo.sh` already prints the hashes.

Ceiling, now measured:

- `live` ↔ `lockfile_hash == current` (opaque string equality)
- `leftover` ↔ `lockfile_hash != current`, including shifted columns, padded hashes, extra `current` fields, and forgotten files
- identity is hash, not id; duplicate ids are two rows
- size is a recorded string; a path column is dropped; 200k digits dump
- `none` means both empty and the member `none`
- no filesystem observation; dummy leftover dirs survive; declared leftover with no files is leftover
- leftover is always rc=0; rc=1 is parse/IO
- the owned record’s hashes are supplied by the rewrite; the CLI will not discover them from a cache tree
- mutation of (1)+(5)+(6) never queued; bytes identical to first MUTATE

Honor KILL. Dreamer ancestry is not protection. First-destroyer MUTATE is not protection once leftover+rc is shown to be caller fingerprint membership. Constitution: a THIN_WRAPPER does not gain a uv fingerprint reconstruction to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Do not merge onto `main`. Do not run uv. Do not merge with freshmiss / lockident. Archive stays under `lineages/candidate-keptfp/`. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/candidate-keptfp-keptfp/`.

KILL
