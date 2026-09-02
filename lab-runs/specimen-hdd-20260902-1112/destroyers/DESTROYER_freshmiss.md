# DESTROYER freshmiss

Date: 2026-09-02

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/freshmiss`

Worktree (byte-identical, sha256 `10d1f7ec2e952b1caaa084773be962093c0241d88b47fa4cdc77bf1f904cc6c3`): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-freshmiss-freshmiss/freshmiss/freshmiss`

Origin claim: given two builds, say whether freshness identity omitted a requested extra output (FRESH-but-missing), and name that extra as `omitted_from_identity`.

Happy path is real. Unit tests (13/13) pass. Specimen-011 first `BUILT` / second `FRESH` / same key `9280cc7e16e9` / `out.sbom` absent is reproduced. That is not enough. The implementation is a string-equal identity plus `status == "FRESH"` plus set-difference of caller-supplied names, and `omitted_from_identity` is that difference labeled as a fingerprint fact.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/freshmiss
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-freshmiss/tests/fixtures
```

No merge with other identity-hash tools. This object is the FRESH-but-missing join, not a fingerprint dump.

---

## What still works

The owned fixture pair, and any other two records the caller has already filled with `status`, `identity`, `requested`, and `present` (or a directory that `--dir` can `exists()`).

```bash
python3 "$CLI" "$FIX/specimen-011-first.rec" "$FIX/specimen-011-second.rec"
```

```text
verdict	FRESH-but-missing
identity	9280cc7e16e9
same_identity	true
first_status	BUILT
second_status	FRESH
requested_extra	out.sbom
missing	out.sbom
omitted_from_identity	out.sbom
rc=0
```

`--dir` overrides a lying `present	out.sbom` when the file is absent on disk. FRESH with the extra actually present is `FRESH-complete`. Same identity, second `BUILT`, extra still absent is `rebuilt` with `omitted_from_identity	none`. Different identity is `identity-changed`. Missing record / not-a-directory `--dir` / unknown field are clean `freshmiss:` errors (rc 1 or 2). Unicode extra names work. Process substitution and `/dev/stdin` work. FIFO records work if a writer exists.

That is the whole useful delta. Attacks below break the identity-omission claim around it, or show the primitive cannot tell an identity miss from a forgotten `present` field.

---

## Implementation

### 1. `omitted_from_identity` is "requested minus present", not "extra outside the key"

README: `omitted_from_identity` is `missing` when the verdict is `FRESH-but-missing`. `compare()` does not intersect with `requested_extra`. A FRESH hit that lost the original output, with no extra requested, is this verdict.

```bash
printf 'status\tBUILT\nidentity\tk\nrequested\tout.bin\npresent\tout.bin\n' > "$TD/first.rec"
printf 'status\tFRESH\nidentity\tk\nrequested\tout.bin\n' > "$TD/same-req.rec"
python3 "$CLI" "$TD/first.rec" "$TD/same-req.rec"
```

```text
verdict	FRESH-but-missing
requested_extra	none
missing	out.bin
omitted_from_identity	out.bin
rc=0
```

No extra was requested. The cache key did not omit `out.sbom`. A file that was in the first identity vanished after a hit. That is eviction / clean / path drift, not the harvest question.

The mixed case is worse. Extra is present; original is gone; the extra is what the tool exists to name; `omitted_from_identity` names the original instead:

```bash
printf 'status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.sbom\n' > "$TD/orig-miss.rec"
python3 "$CLI" "$TD/first.rec" "$TD/orig-miss.rec"
```

```text
verdict	FRESH-but-missing
requested_extra	out.sbom
missing	out.bin
omitted_from_identity	out.bin
```

`out.sbom` was requested, present, and not omitted. The column still claims an identity miss.

### 2. Filename `none` collides with the empty-list sentinel

`fmt_list` prints `"none"` for `[]` and `"none"` for `["none"]`. Extra named `none`, missing:

```bash
printf 'status\tFRESH\nidentity\tk\nrequested\tout.bin\tnone\npresent\tout.bin\n' > "$TD/none-miss.rec"
python3 "$CLI" "$TD/first.rec" "$TD/none-miss.rec"
```

```text
verdict	FRESH-but-missing
requested_extra	none
missing	none
omitted_from_identity	none
rc=0
```

Same extra, actually present (`FRESH-complete`):

```text
verdict	FRESH-complete
requested_extra	none
missing	none
omitted_from_identity	none
rc=0
```

The three list columns are identical. Only `verdict` differs. README says `omitted_from_identity` is `none` when the verdict is *not* `FRESH-but-missing`. Here the verdict *is* `FRESH-but-missing` and the column is still `none`. A pipe that keeps rows where that field is not `none` drops the miss. Tests split on tab and compare `["none"]`, so they cannot see it.

Multiple extras explode into extra TSV columns (`requested_extra` with three names is four fields). `cut -f2` returns only the first extra.

### 3. Forgotten `present` is a false identity miss; empty `present` is a parse error

Omit the `present` field and the directory. Every requested name is missing. Specimen-011 without `present`:

```bash
printf 'status\tFRESH\nidentity\tk\nrequested\tout.bin\tout.sbom\n' > "$TD/no-present.rec"
python3 "$CLI" "$TD/first.rec" "$TD/no-present.rec"
```

```text
verdict	FRESH-but-missing
requested_extra	out.sbom
missing	out.bin	out.sbom
omitted_from_identity	out.bin	out.sbom
rc=0
```

No filesystem observation happened. `out.bin` was never checked. The harvest verdict fires because the caller forgot a field.

Try to declare "I looked, nothing is present" as `present<TAB>`:

```text
freshmiss: .../empty-present.rec:4: expected key<TAB>value
rc=1
```

`raw.strip()` eats the trailing tab, the line becomes `present`, and the parser demands `key<TAB>value`. There is no legal empty `present` list except omitting the field, which is the false miss above. `dir` is the only honest empty-present path.

Declared `present	out.bin	out.sbom` with no `dir` and no `--dir` is believed. Extra absent on disk → `FRESH-complete` rc=0. Tests cover `--dir` override; the default interface does not observe. CANDIDATE.md already required a kept outdir after the tempfile `main()` vanished. The CLI still treats a handwritten `present` list as ground truth.

### 4. `Path.exists` is not "output is present"

`--dir` / `dir` counts anything `exists()` as present: directories, device nodes, broken-symlink negatives, path escape.

Directory occupying `out.sbom`:

```text
verdict	FRESH-complete
requested_extra	out.sbom
missing	none
omitted_from_identity	none
```

Symlink to `/dev/null` named `out.sbom`: `exists() True`, `is_file() False`, `is_char_device() True` → `FRESH-complete`.

`--dir DIR` plus `requested	../../../../../../../../etc/passwd` (passwd exists on this host):

```text
verdict	FRESH-complete
requested_extra	../../../../../../../../etc/passwd
missing	none
omitted_from_identity	none
```

`--dir` is not a root. Absolute requested paths ignore it. `../sib/out.sbom` relative to `--dir` is present if that sibling file exists. A cache hit is then "complete" because `/etc/passwd` or a neighboring tree satisfied `exists()`.

Broken symlink is the one `exists()` case that correctly reports missing. That is an accident of POSIX, not a presence rule.

On this host's case-insensitive volume, `OUT.SBOM` satisfies `out.sbom` and yields `FRESH-complete`. String identity in the record and filesystem identity under `--dir` are different relations; the tool pretends they are one.

### 5. Only exact `FRESH` is a hit; everything else is `rebuilt`

`second.status == "FRESH"` is the entire hit vocabulary. Same identity, extra missing:

| status | verdict | omitted_from_identity |
| --- | --- | --- |
| `FRESH` | `FRESH-but-missing` | `out.sbom` |
| `fresh` | `rebuilt` | `none` |
| `Fresh` | `rebuilt` | `none` |
| `CACHED` | `rebuilt` | `none` |
| `HIT` | `rebuilt` | `none` |
| `UP-TO-DATE` | `rebuilt` | `none` |
| `SUCCESS` | `rebuilt` | `none` |
| `FRESH<TAB>ignored` | `rebuilt` (`second_status` is `FRESH\tignored`) | `none` |

```bash
printf 'status\tfresh\nidentity\tk\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n' > "$TD/fresh-l.rec"
python3 "$CLI" "$TD/first.rec" "$TD/fresh-l.rec"
```

```text
verdict	rebuilt
second_status	fresh
requested_extra	out.sbom
missing	out.sbom
omitted_from_identity	none
rc=0
```

README: other strings "pass through; only `FRESH` is a hit". That is documented. It is still unsupported certainty: `rebuilt` reads as "the cache ran a write", not "we refused this status token". Cargo/ninja/gradle hit words never reach the harvest verdict. Trailing space is stripped (`FRESH ` works); an extra tab column is not.

Duplicate `status` / `identity` lines last-win with no error. First `BUILT` then `FRESH` on one record is a silent FRESH.

### 6. `identity-changed` drops the extra; first identity is unprinted

```bash
printf 'status\tFRESH\nidentity\tOTHER\nrequested\tout.bin\tout.sbom\npresent\tout.bin\n' > "$TD/idchg.rec"
python3 "$CLI" "$TD/first.rec" "$TD/idchg.rec"
```

```text
verdict	identity-changed
identity	OTHER
same_identity	false
requested_extra	out.sbom
missing	out.sbom
omitted_from_identity	none
```

The developer asked two questions: what identity, and which requested outputs were outside it. When the key string moves, the second answer is `none` even though `out.sbom` is still absent. The `identity` row is only the second key. First key is not in the report.

Zero-width space in the second identity (`k` vs `k\u200b`) is `identity-changed` with the extra still missing and omitted `none`. Opaque string equality is the whole identity theory. That is in-boundary. Hiding the missing extra is not.

Swapping the specimen-011 records (second file first) is `rebuilt` with `requested_extra none`: order of argv is the time axis, and the tool will not say so.

### 7. Path spelling and the space-split grammar

`requested	out.bin	./out.sbom` with `present	out.bin	out.sbom`:

```text
verdict	FRESH-but-missing
requested_extra	./out.sbom
missing	./out.sbom
omitted_from_identity	./out.sbom
```

The extra exists under the name the first build would have used. String inequality is a new extra and an identity miss.

`split_values`: if the rest of the line has no tab, it splits on whitespace. `requested	out.bin my file.sbom` becomes extras `my` and `file.sbom`, not `my file.sbom`. Tab-separated `my file.sbom` works, including under `--dir`. README never states the dual grammar. One field, two lexers, silent wrong extras.

`--dir` plus the space-split record against a directory that actually contains `my file.sbom` still reports `missing	my	file.sbom`. The file the human named is present; the names the parser invented are not.

### 8. Misleading exit zero; TSV is not a predicate

All four verdicts are rc=0, including the harvest miss. CANDIDATE.md listed `--check` exit 1 as a suggested mutation. It is still absent. `ls` of a missing extra is rc=1 from `test -e`. This CLI is rc=0 while printing `FRESH-but-missing`. Fine as a printer; hostile as a pipe predicate.

2 MB identity: rc=0, ~2_000_155 bytes of stdout, `identity` row dumps the payload. 5000 extras: `requested_extra` line has 5000 tabs. No cap.

`-` is not stdin (`cannot read -: No such file`). `/dev/stdin` works. Native fixture log does not:

```text
first BUILT extra_exists False key 9280cc7e16e9
second FRESH extra_exists False key 9280cc7e16e9
```

```text
freshmiss: .../log.rec:1: expected key<TAB>value
rc=1
```

`demo.sh` already rewrites that log into records and hardcodes `out.sbom` on the second `requested` line. The extra name the harvest "discovers" is supplied by the rewrite. The fixture log never contains `out.sbom` (CANDIDATE.md surprise). The CLI will not parse the log, and will not guess the name. That is the advertised boundary. It means the `.rec` files are the answer's ingredients, and the CLI is the join.

### 9. Parse edges (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `cannot read ... No such file` |
| directory as record | 1 | `Is a directory` |
| empty file / `/dev/null` | 1 | `missing status` |
| invalid UTF-8 | 1 | `'utf-8' codec can't decode` (caught; UnicodeDecodeError is ValueError) |
| UTF-8 BOM | 1 | `unknown field '\ufeffstatus'` |
| empty identity after strip | 1 | `expected key<TAB>value` (tab stripped) |
| no args / one arg | 2 | argparse |
| JSON object | 1 | `expected key<TAB>value` |
| `--dir` missing or a file or a FIFO | 1 | `not a directory` |
| `--dir` symlink to a dir | 0 | follows |
| comments / blank lines | 0 | skipped; `#requested	out.sbom` drops the extra, then `FRESH-complete` |
| CRLF | 0 | `splitlines` |
| NUL in identity | 0 | identity becomes `k\x00x`; `same_identity false` |
| same file twice (first.rec first.rec) | 0 | `rebuilt`, extras none |

These do not save the omission or presence holes.

---

## Primitive

Reality-stripped operation: parse two TSV maps, `identity` string-equal, `second.status == "FRESH"`, `requested - present`, print a verdict.

Nearest ordinary workflow: the fixture already prints `first BUILT extra_exists False key 9280cc7e16e9` and `second FRESH ... same_key True`. `ls` of the extra path shows absence. `demo.sh` then writes those facts into `.rec` files, including the extra name. Observable capability lost if freshmiss vanishes: the **named join** (`FRESH-but-missing` + which requested name is absent) as one TSV. That join is real when the caller already knows the extra name and has an honest present set. It is not a fingerprint dump, not a cache fixer, not a cargo unit-key reader (research boundary, honored).

That is why this is not KILL: the *question* (same freshness identity, FRESH, requested extra absent — treat that as a miss, not a successful hit) is a debugging object `ls` will not emit. The current embodiment is a specimen-011 record comparator that labels any `requested - present` under exact `FRESH` as `omitted_from_identity`.

The ceiling is already written down, and it is too small for the claim:

- "omitted from identity" = missing names, including vanished primaries and forgotten `present` fields
- `none` means both empty and the filename `none`
- only exact `FRESH` is a hit; `CACHED`/`fresh`/`HIT` are `rebuilt`
- `exists()` is completeness, including directories, `/dev/null`, and `/etc/passwd` via `../`
- declared `present` without a directory is a liar's `FRESH-complete`
- identity is opaque string equality; when it changes, the extra is no longer omitted
- specimen-005 is origin-only; transfer is hand-authored records with cargo-shaped strings, which the CLI will happily mark `FRESH-but-missing` for any two matching identity strings
- the owned fixture's own log is not an input

Do not grow a cargo fingerprint reconstruction to escape this. Do not merge this join into a blob-hash identity tool. Keep the FRESH-but-missing row.

---

## Mutation (what must change)

Keep the object: for two builds, FRESH on the same identity while a newly requested output is absent is not a successful cache hit, and the extra is named.

Do not keep a set-difference that only replays specimen-011's two records.

1. **`omitted_from_identity` is missing ∩ requested_extra.** Vanished primary with no extra is a different verdict (`absent-after-hit` / `FRESH-vanished`), never this one. Extra present + original missing must not put `out.bin` in `omitted_from_identity`. If the mutation cannot tell those apart, a later destroyer should KILL.

2. **`none` is not a list value.** Empty list is a distinct token (`-`, `.`, or a count column). A file named `none` must not render as the empty sentinel. Escape tabs/newlines in names. Repeatable extras stay one field, or get one row per name.

3. **Present is observed or declared-with-source.** Omitting `present` and `dir` is an error, not `FRESH-but-missing`. `present<TAB>` is present=∅, not `expected key<TAB>value`. Declared present without a directory is labeled `declared`; `--dir` is `observed`. Default path must not let a handwritten `present	out.sbom` hide a miss.

4. **`is_file()` (or symlink-to-file), not `exists()`.** A directory, char device, or path that escapes `--dir` is not `FRESH-complete`. Absolute requested paths under `--dir` are an error or are forced inside the root. `./out.sbom` vs `out.sbom` is one name after normalize, or two names with an explicit `path-alias` row — not a silent extra.

5. **Hit vocabulary is declared.** Exact `FRESH` is fine if unknown status is `status-unrecognized` (rc≠0), not `rebuilt`. If `CACHED`/`HIT`/`fresh` are hits, say so. Extra tab on `status` is an error. Duplicate `status`/`identity` is an error or a counted last-win event.

6. **`identity-changed` still lists the missing extra.** Print both identities. `omitted_from_identity` stays `none` if the key moved (cannot blame this identity), but `missing` must remain a first-class row a consumer can grep. argv order is the time axis; document it; swapped specimen-011 records are not `rebuilt` of a write.

7. **rc=1 on `FRESH-but-missing`.** rc=0 only for observed `FRESH-complete` (or a clean `identity-changed` with no missing extra, if that remains a printer). `--check` is not an optional flag on top of a always-zero CLI. Cap huge identity/extra dumps.

8. **Ingest a build log or refuse.** Either parse the fixture's `first BUILT extra_exists ... key` lines (and cargo-like unit+FRESH lines) so `demo.sh` is not a handwritten `.rec` that already contains `out.sbom`, or drop the implication that the CLI named the extra. Still do not guess extra paths that were never requested. Still do not reconstruct fingerprint bytes.

If the mutation cannot do (1)+(3)+(7), the object is still `ls` plus two key strings with extra print, and a later destroyer should KILL.

---

MUTATE
