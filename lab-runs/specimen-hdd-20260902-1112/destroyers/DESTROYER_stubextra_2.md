# DESTROYER stubextra 2

Date: 2026-09-02 15:36 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, KEEP survivor):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-stubextra/stubextra`

sha256 `d4c383845eec66248c39aacf7d20b52bf4f173e1be1366f11744d45a94f5f37a` (4325 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-stubextra-stubextra/stubextra/stubextra` is byte-identical (`cmp` rc=0). Worktree HEAD `fff5e04 ground stubextra from hdd-s071 harvest` on `specimen-hdd/candidate-stubextra-stubextra`. Parent `main` is `432f954`; `stubextra` is not in that tree. Tests 4/4 (`python3 -m unittest discover -s tests -v` → `Ran 4 tests in 0.109s` `OK`, rc=0). `demo.sh` twice: live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log`. Host Python 3.14.5. No merge onto `main`.

Origin (`CANDIDATE.md` / harvest `hdd-s071` / specimen-071): name leftover extra stub on a FRESH hit versus extra produced for this request, and which requested outputs were outside that identity. Kind: USEFUL_COMPOSITION. Owned fixture `cache_build_stub.py` already prints `stub_leftover True`. Rejected: invented cachetool. Constraint: extraedge is poetry extras, not this leftover stub.

First destroyer (`DESTROYER_stubextra.md`) KEEP: owned leftover_stub yes / produced no / extra_outside_identity yes / requested_outside out.sbom; unseen cyclonedx same shape; different key with bytes>0 leftover no produced yes; missing file rc=1; extraedge unknown field `status`; distinct from extraedge / freshmiss-missing. First KEEP is not protection. This cut is extra-present vs extra-omitted on the caller-labeled stubs.

This candidate is a **THIN_WRAPPER** of extra-present (`extra_exists yes`) vs extra-omitted (`extra_exists no`) on records the caller already filled. `leftover_stub` is that bit AND empty bytes AND a requested-flip AND `FRESH` AND same key. `extra_outside_identity` does not read `extra_exists`. `produced_for_request` does not read `extra_exists`. An independent reconstruction that does not import stubextra is **byte-identical** on 30/30 host cases (`stdout_eq=True`, `rc_eq=True`). awk of `extra_exists` membership names the same leftover/outside pair. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-stubextra/stubextra
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-stubextra/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-stubextra-stubextra/stubextra/stubextra
```

Host-executed against the archive. Worktree was not edited. Do not grow a cache hasher / `out.sbom` reader / `cache_build_stub` ingest to escape THIN_WRAPPER. Do not send cachetool theater back to R1. Distinct field names from extraedge / freshmiss are not a derived observation.

---

## What still works

The owned fixture pair, the unseen cyclonedx pair, and any other two TSV events the caller has already filled with `extra_requested` / `extra_exists` / `extra_bytes` / `key` / `status`.

```bash
python3 "$CLI" "$FIX/071-first.rec" "$FIX/071-second.rec"
echo rc=$?
```

```text
key	9280cc7e16e9
same_key	yes
first_status	BUILT
second_status	FRESH
extra_requested_first	no
extra_requested_second	yes
extra_bytes_first	0
extra_bytes_second	0
leftover_stub	yes
produced_for_request	no
extra_outside_identity	yes
requested_outside	out.sbom
rc=0
```

258 bytes. Stderr empty. Unseen `out.cyclonedx`: same twelve rows, leftover yes, requested_outside `out.cyclonedx`, rc=0. Produced fixture (different key, `extra_bytes 12`): leftover no, produced yes, extra_outside no, rc=0. Missing path rc=1. extraedge on these records: `unknown field 'status'`, rc=1. freshmiss: `unknown field 'extra_requested'`, rc=1. Tests 4/4. Demos identical.

That is the whole useful delta. It is also what the caller already typed into `extra_exists` and `extra_bytes`. `demo.sh` states it before the CLI runs:

```text
== nearest: print cache key and extra_exists ==
first BUILT extra_requested no extra_bytes 0
second FRESH extra_requested yes extra_bytes 0 same key
```

Host `python3 specimens/specimen-071/files/cache_build_stub.py` already prints `stub_leftover True`. The CLI will not parse that log.

---

## Implementation

`inspect()` in full:

```python
def inspect(first: dict, second: dict) -> dict:
    same_key = first["key"] == second["key"]
    leftover = (
        same_key
        and not first["extra_requested"]
        and first["extra_exists"]
        and first["extra_bytes"] == 0
        and second["extra_requested"]
        and second["extra_exists"]
        and second["extra_bytes"] == 0
        and second["status"].upper() == "FRESH"
    )
    produced = second["extra_requested"] and second["extra_bytes"] > 0
    outside = second["extra_requested"] and same_key and not produced
    return {
        "first": first,
        "second": second,
        "same_key": same_key,
        "leftover_stub": leftover,
        "produced_for_request": produced,
        "extra_outside_identity": outside,
        "requested_outside": second["extra_name"] if outside else None,
    }
```

`inspect.co_names` is `('upper',)`. `inspect.co_varnames` is `('first', 'second', 'same_key', 'leftover', 'produced', 'outside')`. No `Path`, no `stat`, no `open`. `format_report` does not print `extra_exists`. `extra_name` defaults to `"out.sbom"` when the field is absent. `main` is rc=0 on every well-formed pair, including leftover_stub yes.

Owned fixtures already contain the answer:

```text
# 071-first.rec
extra_requested	no
extra_exists	yes
extra_bytes	0

# 071-second.rec
extra_requested	yes
extra_exists	yes
extra_bytes	0
status	FRESH
```

### 1. THIN_WRAPPER of extra-present vs extra-omitted

Same first record. Second record identical except `extra_exists`:

```text
# extra present (empty stub)     extra_exists	yes
leftover_stub	yes
produced_for_request	no
extra_outside_identity	yes
requested_outside	out.sbom
rc=0

# extra omitted                  extra_exists	no
leftover_stub	no
produced_for_request	no
extra_outside_identity	yes
requested_outside	out.sbom
rc=0
```

`leftover_stub` is `extra_exists` on both sides. `extra_outside_identity` does not move. The harvest name stays `out.sbom`. Flipping the caller-labeled present/omitted bit is the entire leftover delta.

awk of that membership (`extra_exists==yes` both, `extra_bytes==0`, requested flip, `FRESH`, same key) names the same pair:

```text
present  awk_leftover yes  awk_produced no  awk_outside yes
omitted  awk_leftover no   awk_produced no  awk_outside yes
```

Independent reconstruction (parse the same six keys; leftover / produced / outside as above; does not import stubextra) is byte-identical stdout and rc on:

```text
owned 071                         stdout_eq=True rc_eq=True  leftover yes
unseen cyclonedx                  stdout_eq=True rc_eq=True
produced-second (diff key, 12 B)  stdout_eq=True rc_eq=True  leftover no produced yes
same file twice / swap / second twice
present_stub / omitted_exists_no
present_bytes12 / omitted_lying_bytes
present_unrequested / omitted_unrequested
present_built / omitted_built
present_diffkey / omitted_diffkey
present_fresh_lc / present_cached / present_hit
present_name_none / present_noname / present_negbytes
first_also_requested
first_omitted_second_stub / first_omitted_second_omitted
present_1byte
exists_true / exists_false / exists_1 / exists_0
```

30/30. No mismatches.

| extra_exists (second) | extra_bytes | leftover_stub | produced_for_request | extra_outside_identity |
| --- | --- | --- | --- | --- |
| yes (present stub) | 0 | **yes** | no | yes |
| no (omitted) | 0 | **no** | no | yes |
| yes | 12 | no | yes | no |
| no (lying bytes) | 12 | no | **yes** | no |

Same declared request, same key, same FRESH. Only the present/omitted label (and the bytes the caller typed next to it) change the verdict.

### 2. `extra_outside_identity` is extra-omitted, not leftover stub

`outside = extra_requested and same_key and not produced`. `produced` is `extra_requested and extra_bytes > 0`. `extra_exists` is not in that formula.

Extra omitted (`extra_exists no`, `extra_bytes 0`, requested, same key, FRESH): `extra_outside_identity yes`, `requested_outside out.sbom`. That is the freshmiss question (requested extra absent / outside identity). First KEEP called this lineage distinct from freshmiss-missing because the owned extra **exists**. `TRANSFER_s071_freshmiss.md` already recorded that: extra present, so `FRESH-but-missing` fails; the miss is leftover empty stub bytes. This CLI still prints `extra_outside_identity yes` when the extra is omitted. The KEEP distinction is field names on the record, not an observation that leftover stub ≠ missing extra.

Status is a spectator for `extra_outside_identity`. Present stub with `status BUILT` / `CACHED` / `HIT`: leftover no (not `FRESH`), **outside still yes**. Omitted extra with `status BUILT`: leftover no, outside yes. First KEEP's leftover_stub is the `FRESH` AND extra-present conjunction. The "which requested outputs were outside that identity" column is extra-omitted-from-identity (`bytes==0`) including extra omitted from disk.

`first_omitted_second_stub` (`extra_exists no` then `yes`, empty, FRESH): leftover no, outside yes. leftover requires extra-present on **both** events. The second empty extra is not a leftover of an identity write the first record said never happened. The outside column still names `out.sbom`.

Second record twice (`071-second.rec` `071-second.rec`): leftover no (`extra_requested` already yes on first), **outside yes**. Same empty extra, same key, requested on both sides: not leftover, still "outside identity".

Swap (`071-second.rec` then `071-first.rec`): leftover no, produced no, outside no (second `extra_requested` is no). Argv order is the time axis. The CLI will not say so.

### 3. `produced_for_request` is caller-labeled bytes, not extra-present

`produced = extra_requested and extra_bytes > 0`. No `extra_exists`. No same key. No `FRESH`.

Omitted extra with lying `extra_bytes 12`:

```text
extra_exists	no
extra_bytes_second	12
leftover_stub	no
produced_for_request	yes
extra_outside_identity	no
requested_outside	none
rc=0
```

The extra is labeled absent. The CLI reports it was produced for this request. `extra_bytes 1` (present) is the same produced yes. `extra_bytes -1` (present): leftover no, produced no, **outside yes** — negative size is "not produced", so the extra is outside identity.

Owned produced fixture: `extra_bytes 12` on a **different** key, status `BUILT`. produced yes, leftover no, outside no. Production does not require a FRESH hit or a reused identity. It requires the caller to type a positive integer.

Filesystem is not consulted. `extra_exists yes` / `extra_bytes 0` with **no** `out.sbom` on disk: leftover yes, rc=0. `extra_exists no` with a real nonempty `out.sbom` next to the records: leftover no, produced no, outside yes. The CLI has no `--dir`. It never `stat`s the extra.

### 4. `extra_exists` is required as a label and then hidden

Omitting the `extra_exists` field: `stubextra: … missing extra_exists`, empty stdout, rc=1. The present/omitted bit is mandatory input. It is not in the report. A pipe that reads leftover_stub / extra_outside_identity cannot recover whether the extra was present.

Duplicate `extra_exists yes` then `extra_exists no` last-wins: leftover no, outside yes, rc=0. No error. The omitted label silently replaces the present one.

`extra_exists true` / `1` parse as present (leftover yes). `false` / `0` parse as omitted (leftover no, outside yes). `maybe`: `unknown bool 'maybe'`, rc=1. Tokens, not an observed file.

`extra_bytes` omitted: `missing extra_bytes`, rc=1. `extra_bytes zero`: `invalid literal for int()`, rc=1. Forgotten size is an error; forgotten honesty about presence is leftover vs outside as above.

### 5. `requested_outside` is `extra_name` or the default `out.sbom`

Missing `extra_name` field: leftover yes, `requested_outside	out.sbom`. The harvest name the first destroyer treated as discovery is the parser default.

`extra_name none` (present stub): leftover yes, `requested_outside	none`. Empty sentinel and the filename `none` collide. A pipe that drops `none` drops the leftover extra.

`extra_name	out.sbom	out.cyclonedx`: `requested_outside	out.sbom	out.cyclonedx` (two TSV fields). `cut -f2` returns only the first extra.

`extra_name<TAB>` after strip is `expected key<TAB>value`, rc=1. There is no legal empty extra name except omitting the field, which defaults to `out.sbom`.

### 6. Native log and stdin

Specimen-071 observed log:

```text
first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9
second FRESH extra_requested True extra_exists True extra_bytes 0 key 9280cc7e16e9
```

```text
stubextra: …/log.rec:1: expected key<TAB>value
rc=1
```

`demo.sh` already rewrites those facts into `.rec` files, including `extra_name	out.sbom`. The extra the harvest "discovers" is supplied by the rewrite. `cache_build_stub.py` already printed `stub_leftover True`. The CLI will not parse the log, and will not measure extra bytes.

`-` is not stdin (`No such file or directory: '-'`, rc=1). `/dev/stdin` as FIRST works. Process substitution works. Symlink to the first record matches owned. Directory as record: `Is a directory`, rc=1. `/dev/null`: `missing status`, rc=1. JSON: `expected key<TAB>value`. UTF-8 BOM: `unknown field '\ufeffstatus'`. Invalid UTF-8: codec error, rc=1. Spaces not tabs: `expected key<TAB>value`. Unknown field `present`: refused. Comments / blanks / CRLF: harvest. No args / one arg: argparse rc=2. `--help` rc=0.

200_000-char second key: rc=0, stdout 251 bytes, `same_key no`, leftover no. The report prints **first** key only. Second identity is dropped when they differ. No cap.

### 7. Misleading exit zero

leftover_stub yes is rc=0. extra_outside_identity yes is rc=0. produced yes is rc=0. The first KEEP already treated missing path as rc=1 and harvest as rc=0. Fine as a printer of labels; hostile as a pipe predicate for "this extra is a leftover stub". `test -s out.sbom` is rc=1 on the owned empty stub. This CLI is rc=0 while printing leftover yes.

`first_status` is printed and unused in leftover (only `second.status.upper() == "FRESH"`). `fresh` lowercase is leftover yes. `CACHED` / `HIT` / `BUILT` are leftover no and extra_outside yes.

---

## Primitive

Reality-stripped operation: parse two TSV maps; `same_key` is string equality of `key`; `leftover_stub` is extra-present (`extra_exists`) on both sides AND `extra_bytes==0` AND requested-flip AND second `FRESH`; `produced_for_request` is `extra_requested and extra_bytes > 0`; `extra_outside_identity` is `extra_requested and same_key and not produced`; print first key and the caller's `extra_name` (default `out.sbom`); rc=0.

Nearest ordinary workflow: the fixture already prints `stub_leftover True`. `ls -l out.sbom` plus `test -s` names empty present extra. awk of `extra_exists` / `extra_bytes` / `extra_requested` on the `.rec` files the demo writes names leftover vs produced vs outside. Observable capability lost if stubextra vanishes: **none**. The harvest question (was this extra produced for the FRESH request, or leftover empty bytes from the identity write?) is real. This embodiment asks it of `extra_exists` / `extra_bytes` / `extra_requested` the caller already typed.

That is why this is KILL, not MUTATE. First KEEP survived because extraedge cannot parse `status` and freshmiss-missing wants absence. Extra-present vs extra-omitted on those same caller-labeled stubs is the leftover column. `extra_outside_identity` is extra-omitted (bytes==0) including extra omitted from disk. Adding a cache-key hasher / outdir walk / `cache_build_stub` ingest would be implementing the composition this artifact failed to embody — a new harvest, not a patch of bool lookup. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Hardcoded ceiling:

- leftover_stub = extra-present (`extra_exists` both) AND extra_bytes==0 AND requested-flip AND FRESH AND same key
- extra_outside_identity does not read extra_exists; omitted extra and present empty stub share that column
- produced_for_request does not read extra_exists, same_key, or FRESH; lying bytes on an omitted extra report produced
- extra_exists is a required label, last-win, not printed, never `stat`ed
- extra_name defaults to `out.sbom`; filename `none` collides with the empty sentinel
- rc=0 on leftover / outside / produced; rc=1 is parse/IO
- native `first BUILT extra_requested …` log is not an input; demo.sh already contains the answer
- extraedge / freshmiss field-name mismatch is not a new primitive
- the CLI will not hash inputs, will not read `out.sbom`, will not run `cache_build_stub.py`

Do not grow a cache hasher to escape THIN_WRAPPER. Do not merge this join onto `main`. Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection.

---

KILL
