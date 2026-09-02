# DESTROYER extraedge (2)

Date: 2026-09-02 14:17 JST
RUN_ID: specimen-hdd-20260902-1112

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-extraedge/extraedge`

sha256 `cb58d2e26833205b49486d65ea4de8fcb6826486473e023abaa6c0817ae49881` (11139 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-extraedge-extraedge/extraedge/extraedge` is byte-identical. Worktree HEAD `9ed3189` on `specimen-hdd/candidate-extraedge-extraedge`. Parent `main` is `432f954`; `extraedge` is not in that tree. Tests 21/21. `demo.sh` ×2 identical and matches archived `demo-1.log`. Host Python 3.14.5. Poetry is not executed. No merge onto `main`.

First destroyer (`DESTROYER_extraedge.md`) MUTATE applied. Empty-resolved-as-miss is gone and is not re-attacked. This pass attacks the **new mapping**: extras table `extra NAME TARGET`, missed = declared whose mapped targets are all absent, empty list `.`, rc=1 on miss, identity mismatch rc=1.

Origin claim after mutate: given two records of one package version and an extras table, name declared extras whose mapped extra-edge targets did not attach, and extra-edges that attached only on the second record. Specimen-021 / hdd-gitextra. Kind: USEFUL_COMPOSITION.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-extraedge/extraedge
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-extraedge/fixtures
```

This candidate is a **THIN_WRAPPER** of the extras table the caller already wrote. `missed_declared()` is dict lookup plus `any(target in resolved)`. An independent reconstruction of that join is **byte-identical** to extraedge on 24/24 host cases (`stdout_eq=True`, `rc_eq=True`). `join(1)` of the fixture’s `extra` / `declared` / `resolved` columns yields the owned harvest. Decision: **KILL**.

---

## What still works

The owned fixture pair, add-lock as FIRST, the unseen pair, swapped 021, identity mismatch, extra named `none`, two extras one attach, `-` stdin, unmapped refuse, forgotten `resolved` error, and the input caps. Mutation checklist items fire. `rg` finds no `poetry` / `pyproject` / `lock` / `.toml` in the CLI.

```bash
python3 "$CLI" "$FIX/021-edit.rec" "$FIX/021-add.rec"
echo rc=$?
```

```text
package_a	sqlalchemy
version_a	2.1.0b1.dev0
package_b	sqlalchemy
version_b	2.1.0b1.dev0
same_package	yes
map	postgresql	psycopg2
declared	postgresql
resolved_a	.
resolved_b	psycopg2
missed_a	postgresql
missed_b	.
attached_b	psycopg2
rc=1
```

```bash
python3 "$CLI" "$FIX/021-add.rec" "$FIX/021-add.rec"; echo rc=$?
```

```text
map	postgresql	psycopg2
resolved_a	psycopg2
missed_a	.
attached_b	.
rc=0
```

```bash
python3 "$CLI" "$FIX/unseen-edit.rec" "$FIX/unseen-add.rec"; echo rc=$?
```

```text
map	feat	widget
missed_a	feat
attached_b	widget
rc=1
```

`python3 "$CLI" - "$FIX/021-add.rec" < "$FIX/021-edit.rec"` is the same TSV, rc=1. `-` as SECOND is the same. `/dev/stdin` as FIRST is the same. Symlink to the edit record is the same. FIFO with a writer is the same. `<(cat "$FIX/021-edit.rec")` is the same. Unicode extras (`機能` / `依存`) work. Extra named `none` / `-` survive. `declared	my extra` is one name. Comments, blank lines, CRLF parse. Missing path / empty file / `/dev/null` / unknown field / missing package, version, or resolved: `extraedge:` on stderr, empty stdout, rc=1. No args / one arg: argparse rc=2. `--help` rc=0.

That is the whole useful delta. It is also what `join` of three columns the caller already filled already does. Attacks below show the extras table is the answer key, not a derived extra→dep map.

---

## Implementation

`missed_declared` in full:

```python
def missed_declared(declared, resolved, extras):
    present = set(resolved)
    missed = []
    for extra in declared:
        targets = extras[extra]
        if not any(target in present for target in targets):
            missed.append(extra)
    return missed
```

`inspect.co_names` is `('package', 'version', 'merge_extras', 'unique', 'declared', 'missed_declared', 'resolved', 'values', 'set')`. `missed_declared.co_names` is `('set', 'any', 'append')`. `attached_only_second` is `resolved_b − resolved_a` intersected with the extras-table **values**. No file except the two TSV records is read.

Owned fixtures already contain the map the harvest needs:

```text
# 021-edit.rec and 021-add.rec both
extra	postgresql	psycopg2
```

`demo.sh` states it before the CLI runs:

```text
declared extra postgresql maps to extra-edge psycopg2; edit-lock resolved empty; add-lock resolved psycopg2
(without an extras table, extra names and extra-edge package names are different vocabularies)
```

### 1. THIN_WRAPPER of the extras table the caller already wrote

Independent reconstruction (`/tmp/extraedge-d2/thin_join.py`, does not import extraedge): parse `extra NAME TARGET…` into a dict; miss iff no target is in that record’s `resolved`; `attached_b` is resolved-only-on-B tokens that are dict values; identity mismatch zeros harvest columns. Byte-identical stdout and rc on every well-formed case run:

```text
owned 021                 stdout_eq=True rc_eq=True  extraedge rc=1
add-lock as FIRST         stdout_eq=True rc_eq=True  extraedge rc=0
unseen                    stdout_eq=True rc_eq=True
swapped 021               stdout_eq=True rc_eq=True
unmapped / forgotten extra stdout_eq=True rc_eq=True
forgotten extra+declared  stdout_eq=True rc_eq=True  extraedge rc=0
lying map -> widget       stdout_eq=True rc_eq=True
lying map -> typing-extensions stdout_eq=True
identity map postgresql->postgresql stdout_eq=True
honest 021 typing-extensions stdout_eq=True
multi-target over-broad   stdout_eq=True rc_eq=True  extraedge rc=0
multi-target any-of hit   stdout_eq=True rc_eq=True
two extras one attach     stdout_eq=True rc_eq=True
two declared, one extra line stdout_eq=True
identity mismatch pkg/ver stdout_eq=True
extra named none / -      stdout_eq=True
orphan map                stdout_eq=True rc_eq=True  extraedge rc=0
map only on FIRST / SECOND stdout_eq=True
unicode / space name / wrongmap stdout_eq=True
```

24/24. No mismatches.

`join(1)` of the owned extras table against declared, then membership of the target in resolved, names the same harvest:

```text
join declared to map:  postgresql	psycopg2
awk_missed_a=postgresql
awk_attached_b=psycopg2
extraedge missed_a	postgresql
extraedge attached_b	psycopg2
```

Same declared + same resolved, **only the extras table changes the verdict** (A `resolved typing-extensions`, B `resolved psycopg2`, `declared postgresql`):

| extras table | missed_a | attached_b | rc |
| --- | --- | --- | --- |
| `postgresql → psycopg2` | postgresql | psycopg2 | 1 |
| `postgresql → typing-extensions` | `.` | `.` | 1 (missed_b) |
| `postgresql → widget` | postgresql | `.` | 1 |
| `postgresql → psycopg2 typing-extensions` | `.` | psycopg2 | **0** |
| (omitted) | unmapped postgresql; harvest `.` | `.` | 1 |

The CLI does not know that sqlalchemy’s `postgresql` extra-edge is `psycopg2`. It knows whatever `extra` line the caller typed. That line is the answer key.

### 2. Unmapped extras / forgotten extra field

Honest 021 facts (`resolved typing-extensions` then `psycopg2`) with **no** `extra` field:

```bash
python3 "$CLI" unmapped-a.rec unmapped-b.rec; echo rc=$?
```

```text
declared	postgresql
resolved_a	typing-extensions
resolved_b	psycopg2
unmapped	postgresql
missed_a	.
missed_b	.
attached_b	.
rc=1
```

Refuse, not a derived miss. The first destroyer’s KILL trigger (“still prints `missed_a none` for typing-extensions”) is avoided only when the caller writes `extra	postgresql	psycopg2`. Without that field the harvest columns are `.`.

Forgotten extra **and** forgotten declared, resolved still differs (`psycopg2` appears on B):

```text
declared	.
resolved_a	.
resolved_b	psycopg2
missed_a	.
attached_b	.
rc=0
```

The extra-edge that attached is invisible. `attached_b` is not “new resolved tokens”. It is “new resolved tokens that the extras table listed as targets”.

`extra` present for a **different** name (`mysql → mysqlclient`) while `declared postgresql`:

```text
map	mysql	mysqlclient
declared	postgresql
resolved_b	psycopg2
unmapped	postgresql
missed_a	.
attached_b	.
rc=1
```

The unused map is echoed. The missing map is named `unmapped`. Nothing is derived.

Add-lock as FIRST with the extras table **stripped** (`declared postgresql`, `resolved psycopg2` on both sides):

```text
unmapped	postgresql
missed_a	.
attached_b	.
rc=1
```

The mutation test `test_add_lock_as_first_is_not_a_miss` is rc=0 only because `021-add.rec` contains `extra	postgresql	psycopg2`. Strip that line and a successful attach is not a hit; it is `unmapped`.

### 3. extra NAME with multiple targets

`any(target in present)`: one present target is a full hit.

`extra	postgresql	psycopg2	psycopg2-binary` and only `psycopg2-binary` in resolved: `missed_a .`, rc=0.

Over-broad map on honest 021 — `extra	postgresql	psycopg2	typing-extensions`, A has `typing-extensions`, B has `psycopg2`:

```text
map	postgresql	psycopg2	typing-extensions
resolved_a	typing-extensions
resolved_b	psycopg2
missed_a	.
missed_b	.
attached_b	psycopg2
rc=0
```

`postgresql` never attached its extra-edge on A. `missed_a` is `.`. rc=0. The pair is a successful attach because the caller listed a base require as a target. Same declared/resolved with a tight map (`postgresql → psycopg2` only) is `missed_a postgresql`, rc=1. Multi-target is still membership of caller-written names.

Tight multi-target (`psycopg2` + `psycopg2-binary`) with A `typing-extensions`: `missed_a postgresql`, `attached_b psycopg2`, rc=1 — the honest miss, again because the caller did not list `typing-extensions`.

### 4. Map that lies

`extra	postgresql	widget` while B actually resolved `psycopg2`:

```text
map	postgresql	widget
resolved_a	.
resolved_b	psycopg2
missed_a	postgresql
missed_b	postgresql
attached_b	.
rc=1
```

B **has** `psycopg2`. Both sides miss. `attached_b` is `.` because `psycopg2 ∉ {widget}`. A lying map hides the extra-edge that appeared and reports a miss on a successful add-lock.

`extra	postgresql	typing-extensions` on honest 021:

```text
map	postgresql	typing-extensions
resolved_a	typing-extensions
resolved_b	psycopg2
missed_a	.
missed_b	postgresql
attached_b	.
rc=1
```

A is a false hit (`typing-extensions` present). `attached_b` does not name `psycopg2`. rc=1 is `missed_b`, not “the extra-edge attached later”.

Identity map `extra	postgresql	postgresql` with both resolved `psycopg2` (successful add-lock):

```text
map	postgresql	postgresql
resolved_a	psycopg2
missed_a	postgresql
missed_b	postgresql
attached_b	.
rc=1
```

That is the README set-difference the first destroyer forbade (`postgresql ∉ {psycopg2}`), now opt-in via the extras table. The CLI will report whatever join the caller encoded.

Conflicting maps on the **same** package (`feat → widget` vs `feat → gadget`): empty stdout, `extraedge: conflicting extra-edge map for 'feat': ['widget'] vs ['gadget']`, rc=1. The tool checks that the two answer keys agree. It does not check either against the world.

### 5. same_package no

Different package (`notsqlalchemy`), different version (`2.0.0`), `SQLAlchemy` vs `sqlalchemy`: all

```text
same_package	no
identity	mismatch
declared	.
resolved_a	.
resolved_b	.
missed_a	.
missed_b	.
attached_b	.
rc=1
```

Harvest columns are `.`. Second identity is printed (`package_b` / `version_b`). Mutation (3) holds.

Conflicting maps on **mismatched** packages do not merge: identity mismatch, no conflict error. The extras table is ignored once `package`/`version` strings differ. `attached_b` cannot fill from another node.

Extra columns on `package`: `extra columns on package`, rc=1, empty stdout. Duplicate `package` / `version` / `resolved` / `extra NAME`: errors. Mutation (3) last-win is gone.

### 6. extra named none

`declared none`, `extra	none	nonepkg`, A empty, B `nonepkg`:

```text
map	none	nonepkg
declared	none
missed_a	none
resolved_a	.
attached_b	nonepkg
rc=1
```

Extra named `-` is the same shape (`dashpkg`). Extra named `.` is a parse error: `empty-list marker cannot mix with names`, rc=1. Empty list is `.` on output. Mutation (4) holds for names; `.` cannot be an extra.

### 7. add-lock as FIRST

`$FIX/021-add.rec` twice: `missed_a .`, `attached_b .`, rc=0. Mapped extra-edge present; not a miss — **because the fixture’s extras table says `postgresql → psycopg2` and `resolved` is `psycopg2`**. Same records without the `extra` line: `unmapped postgresql`, rc=1 (§2).

### 8. two extras one attach

Caller writes two extra lines. A resolved `psycopg2` only, B both deps:

```text
map	postgresql	psycopg2
map	mysql	mysqlclient
declared	postgresql	mysql
resolved_a	psycopg2
resolved_b	psycopg2	mysqlclient
missed_a	mysql
attached_b	mysqlclient
rc=1
```

Two declared extras, **only** `postgresql` mapped:

```text
map	postgresql	psycopg2
declared	postgresql	mysql
resolved_b	psycopg2	mysqlclient
unmapped	mysql
missed_a	.
attached_b	.
rc=1
```

`mysqlclient` attached. Harvest is `.`. Partial extras are first-class only when the caller also wrote the second extras-table row. One missing `extra` line and the tool will not name the extra that still has no target.

### 9. swapped records

`021-add.rec` then `021-edit.rec`:

```text
resolved_a	psycopg2
resolved_b	.
missed_a	.
missed_b	postgresql
attached_b	.
rc=1
```

Argv order is the time axis. The CLI will not say so. A later empty resolved is `missed_b`, not “the extra-edge detached”.

Map on FIRST only, or on SECOND only, is enough: `merge_extras` unions both records. The answer key may arrive on either side and still explain the other. Putting `extra	postgresql	psycopg2` only on the add-lock still makes the edit-lock a mapped miss.

Orphan map (extras table, **no** `declared`):

```text
map	postgresql	psycopg2
declared	.
resolved_a	.
resolved_b	psycopg2
missed_a	.
attached_b	psycopg2
rc=0
```

`attached_b` fires for a token nobody requested. rc=0. The extras table is sufficient for `attached_b` even when nothing was declared; declared without extras is `unmapped` and `attached_b` is `.`.

### 10. huge tables

256 extras, all unresolved: rc=1, 7005-byte stdout, **256 `map` lines** (first `map	e0	t0`, last `map	e255	t255`), `missed_a` has 256 TSV fields. The printer dumps the answer key.

257 extras: `more than 256 extras`, rc=1, empty stdout.
257 declared names on one line: `more than 256 extras`.
`extra NAME` with 257 targets: `more than 256 extra-edge targets`.
Extra name 257 chars: `extra name exceeds 256 characters`.
Version 1025 chars: `version exceeds 1024 characters`.
Input 74763 bytes: `input exceeds 64000 bytes`.

Caps hold. Mutation (5) huge-dump ceiling is parse-time, not a derived map.

### 11. stdin

`-` is stdin (one side). Both `-`: `extraedge: stdin used twice`, rc=1, empty stdout. `/dev/stdin` as FIRST with the edit record on the pipe matches owned. Symlink matches. FIFO with a writer matches. FIFO with no writer blocked until a 2s timeout (no stdout, no stderr). Directory as record: `Is a directory`, rc=1. Missing path: `No such file or directory`, rc=1.

### 12. Parse around the extras table

`extra` with no target: `extra needs name and extra-edge target`.
Duplicate `extra feat`: `duplicate extra 'feat'`.
Empty extra name: `empty extra name`.
`extra	feat	.	widget`: `empty-list marker cannot mix with names`.
NUL in extra name: `NUL in extra name`.
Forgotten `resolved`: `missing resolved` (not a harvest miss).
Spaces instead of tabs: `expected key<TAB>value`.
UTF-8 BOM: `unknown field '\ufeffpackage'`.
Invalid UTF-8: `'utf-8' codec can't decode byte 0xff'`.
JSON object: `expected key<TAB>value`.
Unknown field: `unknown field 'extra_field'`.

Lexer is one path: tab-separated names. Mutation (4)/(5) parse errors hold. They do not make the extras table derived.

---

## Primitive

Reality-stripped operation: parse two TSV maps; `same_package` is string equality of `package` and `version`; `extras[name] = targets` from caller-written `extra` lines; `missed_*` is declared names whose targets are all absent from that record’s `resolved`; `attached_b` is `resolved_b − resolved_a` ∩ extras-table values; print both identities; rc=1 on miss, unmapped, mismatch, or parse error.

Nearest ordinary workflow: `join` of the three columns already in the record (`declared`, `extra NAME TARGET`, `resolved`), or `grep` of the extra-edge the caller wrote. `demo.sh` tells the caller `postgresql maps to psycopg2` before the CLI runs. REALITY.md’s nearest operation is “read pyproject extras and the lock”; this CLI reads neither.

Observable capability lost if extraedge vanishes: **none**. The extras table is already in the input. Membership is `in`. Identity is `==`. Unmapped is `name not in extras`. The named join (`missed_a` + `attached_b` on a reused node) is `join(1)` plus those tests, packaged as TSV.

That is why this is KILL, not MUTATE. The *question* (this extra was declared on a reused package node, its extra-edge did not attach, later the same node grew that edge) is a real debugging object `poetry show` will not emit. This embodiment does not ask it of pyproject, a lock, or package extras. It asks whether the extra-edge names the caller typed into `extra NAME TARGET` are members of the resolved lists the caller also typed. Adding a poetry extras walk / pyproject parse / lock dump would be implementing the composition this artifact failed to embody — a new harvest, not a patch of dict lookup. The first destroyer already forbade growing `Provider.complete_package`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

The mutation did (1)+(2)+(3) of DESTROYER_extraedge.md **as record fields**. (1) is an extras table the caller writes. (2) names a partial miss only when the caller also wrote the second `extra` line. (3) gates identity. That is a stricter printer of the answer key, not a map.

Hardcoded ceiling:

- extras table is caller-written `extra NAME TARGET…`; it is not derived
- `missed_*` = `not any(target in resolved)` on that dict
- `attached_b` is gated by extras-table **values**; without the table, new resolved tokens are silent
- unmapped declared extras refuse (`unmapped`, harvest `.`); they are not guessed
- a lying / over-broad / identity map is believed and fully determines both harvest columns
- `same_package no` zeros harvest; conflicting maps on a mismatch are not even compared
- empty list is `.`; extra named `none` / `-` survive; `.` cannot be a name
- rc=1 on miss, unmapped, mismatch, or parse error; rc=0 for orphan map + attached_b and for over-broad false hits
- forgotten `resolved` is an error; forgotten `extra` is `unmapped` if anything was declared
- the owned fixture’s `extra	postgresql	psycopg2` is a pre-answer; specimen facts still include `typing-extensions`
- the CLI will not parse a lock or a pyproject

Do not grow a poetry extras solver to escape THIN_WRAPPER. Do not merge this join onto `main`. Honor KILL. Dreamer ancestry is not protection.

---

KILL
