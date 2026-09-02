# DESTROYER envlayers 2

Date: 2026-09-02 15:42 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, POST-MUTATE dotenv-subset / caller inherited / presence):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/envlayers`

sha256 `f24acac0c3ccd29a5aa866d2451b1b6875c17ff33f48ae36ee128829c159d7ff` (11566 bytes). Matches `lineages/candidate-envlayers/MUTATE.md` after. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers/envlayers` is byte-identical (`cmp` rc=0). HEAD `0939739 MUTATE envlayers: dotenv subset, caller inherited, presence labels.` Branch `specimen-hdd/candidate-envlayers-envlayers`. Parent `main` is `432f954`; `envlayers` is not in that tree. Host Python 3.14.5. No merge onto `main`. Worktree was not edited.

`python3 tests/test_envlayers.py -v` → 34/34 OK (archive and worktree). `./demo.sh` ×2 live logs byte-identical to archived `demo-1.log` / `demo-2.log`. Worktree `selfcheck.py` ok. Direct exec, `python3 envlayers`, and worktree `envlayers.py` (850-byte fold) produce identical owned stdout.

First destroyer (`DESTROYER_envlayers.md`) MUTATE. Applied cut: assignment events, declared dotenv subset, inherited caller-supplied (not `os.environ` default), presence+source, one CLI, clean errors. First-selection KEEP was lineage-only (peel parser; not a PATH install). MUTATE leftover: if a later destroyer still sees only `printenv` of caller-labeled layers / two CLIs / `os.environ` default inherit, **KILL**. Do not add envprobe. Do not pretend the table discovered which merge a third-party tool used.

This pass host-executed those three leftover conditions and the mutate claims (assignment events / one CLI / empty-vs-unset). Two CLIs: closed. Default inherit: closed. Empty-vs-unset and assignment events: real. The object is still `printenv` of caller-labeled layers plus two hardcoded `if v:` vs always-assign policies. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/envlayers
SPEC=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-010/files/loader.py
```

Host-executed against the archive. Grounder forbids attach. Do not grow envprobe. Do not send a third loader back to R1.

---

## Honor-KILL checklist (leftover)

| leftover | host | still? |
| --- | --- | --- |
| two CLIs | archive has only `./envlayers`; worktree `envlayers.py` re-exports that file; `python3 envlayers` / direct exec / `envlayers.py` stdout IDENTICAL on `KEY=` + inherited `/x` | no |
| `os.environ` default inherit | `env KEY=live python3 "$CLI" KEY` → `inherited None absent none` / `process 'live' present os.environ` | no |
| `printenv` of caller-labeled layers | inherited is `--inherited`; process is this CLI `os.environ`; skip_empty/assign are two hardcoded policies on that map + file; after a real skip-empty loader, `printenv KEY` is `/x` and envlayers only shows `file ''` because the caller passed `--inherited KEY=/x --file` | **yes** |

Mutate claimed assignment events / one CLI. Host-verified. That is not protection once the leftover `printenv` condition still holds.

---

## What the mutation still holds

Owned 010: inherited `'/x'`, file empty-assignment `''`, skip_empty `'/x'` source `inherited`, assign `''` source `file-empty`, process unset. Quoted `KEY=""` is empty, not `'""'`. Duplicate `KEY=fromfile` then `KEY=`: `file_n 2`, skip_empty `'fromfile'` source `file`, not inherited. Default inherited is not a process copy. Process `env -u KEY` vs `env KEY=` is unset vs empty. One program.

```bash
printf 'KEY=\nOTHER=2\n' > /tmp/el.env
env -u KEY python3 "$CLI" --inherited KEY=/x --inherited OTHER=1 --file /tmp/el.env KEY
```

```text
key	KEY	query	
inherited	'/x'	present	caller
file	''	empty-assignment	text
skip_empty	'/x'	present	inherited
assign	''	empty	file-empty
process	None	unset	os.environ
file_n	1	assignments	
policies_disagree	true		
```

```bash
printf 'KEY=fromfile\nKEY=\n' > /tmp/dup.env
env -u KEY python3 "$CLI" --inherited KEY=/x --file /tmp/dup.env KEY
```

```text
file	''	empty-assignment	text
skip_empty	'fromfile'	present	file
assign	''	empty	file-empty
file_n	2	assignments	
```

```bash
env KEY=live python3 "$CLI" KEY
env -u KEY python3 "$CLI" KEY
env KEY= python3 "$CLI" KEY
```

```text
inherited	None	absent	none
process	'live'	present	os.environ

process	None	unset	os.environ
process	''	empty	os.environ
```

`printenv` on this host: unset rc=1 empty stdout; `KEY=` rc=0 prints a newline; `KEY=/x` prints `/x`. Process empty-vs-unset is a `printenv` of *this* CLI. The file's `KEY=` is the column `printenv` cannot see — only after the caller already labeled inherited and pointed at the file.

That is the whole useful delta after mutation. Attacks below show it is still caller-labeled layers.

---

## Implementation

### 1. After a real skip-empty loader, printenv still cannot see `KEY=`; envlayers cannot see it either unless the caller already knew

Host skip-empty loader (specimen `if v:`), inherited `KEY=/x`, file `KEY=`:

```bash
# loader execs printenv KEY after skipping empty assignments
env KEY=/x python3 skip_loader.py     # printenv → /x  rc=0
env KEY=/x python3 "$CLI" --inherited KEY=/x --file file.env KEY
```

```text
printenv KEY=/x
envlayers file	''	empty-assignment
envlayers skip_empty	'/x'	present	inherited
envlayers process	'/x'	present	os.environ
```

envlayers reports the file empty-assignment because `--inherited KEY=/x --file file.env` restated the world. It did not observe the loader. Drop `--inherited` and the same process with `KEY=/x` in the environment shows `inherited None` / `skip_empty None` / `process '/x'` — the file empty-assignment is still printed (the file was passed), but skip_empty no longer keeps `/x` unless the caller labeled it. The skip-empty column is a function of the labeled map, not of what the child inherited.

### 2. Two hardcoded policies; replica 20/20 IDENTICAL

`load_skip_empty` is `if value: out[k]=v`. `load_assign` always assigns. `file_n` is `len(key_events)`. `skip_empty_source` is `file` iff a non-empty file assignment exists. An independent reconstruction of that grammar + those two merges is byte-identical to CLI stdout on 20/20 host cases (owned 010, absent key, duplicate empty, `KEY=""`, `export`, comments, BOM, `KEY=0`, quoted space, unquoted space, three dups, empty-then-value, omitted `--file`, process unset/empty/live).

Naive `loader.py` `partition("=")` matches owned `KEY=` (`skip '/x'` / `assign ''`) and **disagrees** on `KEY=""` (`skip '""'`). The mutate peeled that parser. After the peel, the object is still the two policies.

### 3. Inherited is caller-supplied; process is this CLI

`--from-process-env` copies `os.environ` into inherited (`source process-copy`). Combined with `--no-process-env`, inherited stays empty (the default). `--process KEY=` injects the process column (`source injected`) while live `KEY=live` remains in `os.environ`. None of these attach. `process` without `--process` is `dict(os.environ)` of the debugger.

### 4. Presence labels are real; they label the calculator

Omitted `--file`: `file None omitted none`. Empty file and `/dev/null`: `file None absent text`. Missing path: `envlayers: file not found: PATH` rc=1, no Errno, no traceback. Directory: `is a directory`. Invalid UTF-8: `not utf-8`. `export KEY` without `=`: `not an assignment` rc=1. `# KEY=secret` is not a key. Query `# KEY` is `bad key` rc=2.

`--inherited KEY=` vs omitted: `inherited '' empty caller` vs `inherited None absent none`. That is empty-vs-unset of the overlay the caller typed.

### 5. Remaining parser dialect (not a reason to mutate)

| input | host |
| --- | --- |
| `KEY=value # comment` | value `'value # comment'` (inline comments not in the declared subset) |
| `KEY= ` (unquoted spaces) | empty-assignment after `strip` |
| `KEY=" "` | value `' '` (truthy; skip_empty overwrites inherited) |
| `KEY=0` | value `'0'`; skip_empty keeps `'0'` (`if v:` is Python truthiness, the specimen) |
| `FOO-BAR=1` | `bad key` rc=1 |
| `KEY+=x` | `bad key: 'KEY+'` rc=1 |
| JSON | `not an assignment` rc=1 |
| NUL in UTF-8 | `nul in assignment` rc=1 |
| `--file -` | `file not found: -` rc=1 |
| `/dev/stdin` with `KEY=` | works (`empty-assignment`) |
| FIFO, no writer | blocks in `open()` (observed 1.5s timeout) |
| query `KEY\n` | `KEY_RE` `$` matches before a trailing newline; TSV row splits (`key\tKEY\n\tquery\t`) rc=0 |

Huge values cap at 256 + `…` (256 no ellipsis, 257 yes). Display path only.

---

## Primitive

Reality-stripped operation: parse a declared dotenv subset; merge a caller-supplied inherited map with `if v:` vs always-assign; print this process `os.environ.get` plus presence/source/`file_n`.

Nearest ordinary workflow: read `specimens/specimen-010/files/loader.py` and `printenv`. After mutate, also a 40-line dotenv subset so `KEY=""` is empty. Observable capability lost if envlayers vanishes: labels on a merge the caller already specified. It does not attach, does not name which policy a third-party tool used, does not observe inherited from a parent.

That is why this is KILL, not MUTATE. The *question* (empty assignment vs unset, and which of two merge rules won) is still a real debugging object. This embodiment asks it of `--inherited` and `--file` the operator already has. Adding a live attach / envprobe / third loader is the leftover the first destroyer forbade, and the grounder forbade attach at harvest. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First-selection KEEP was lineage-only (peel parser). The parser peeled. First MUTATE is not protection.

Hardcoded ceiling:

- skip_empty = last non-empty file assignment else inherited
- assign = last file assignment including empty
- inherited default empty; `--from-process-env` is opt-in copy of this process
- process = this CLI `os.environ` unless `--process` injects a snapshot
- two policies only; last-wins-then-skip remains rejected
- no attach, no third-party loader, no “match this printenv snapshot” beyond `--process`

Do not add envprobe. Do not add a third policy. Do not merge onto `main`. Honor KILL. Dreamer ancestry is not protection.

Archive stays under `lineages/candidate-envlayers/`.

KILL
