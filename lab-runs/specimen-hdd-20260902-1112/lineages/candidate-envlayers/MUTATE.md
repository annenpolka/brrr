# MUTATE envlayers (applied 2026-09-02)

From `destroyers/DESTROYER_envlayers.md` after MUTATE (not KILL of the
question). First-selection KEEP was lineage-only.

```yaml
origin:
  method: hdd
  trial: hdd-env-empty
  specimens: [specimen-010]
  mutation: dotenv-subset parse; caller inherited; presence+source; one CLI
  parent: candidate-envlayers
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers
branch: specimen-hdd/candidate-envlayers-envlayers
parent_commit: 29ccacf87ee3a8ddd6e01250efe5cedb6263c2ab
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/
cli_sha256_before: 80d74d5dd77e5b7bf2c39f3ec6b7cf110b9467467664fba52ca89e476804b14c
cli_bytes_before: 5437
cli_sha256_after: f24acac0c3ccd29a5aa866d2451b1b6875c17ff33f48ae36ee128829c159d7ff
cli_bytes_after: 11566
```

Not merged to `main`. No attach. No envprobe.

`python3 tests/test_envlayers.py -v` twice — 34/34 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.
`python3 selfcheck.py` ok.

Kept FIX: missing `--file` is `envlayers: file not found: PATH` (rc=1), no
`[Errno 2]`, no traceback. Directory / invalid UTF-8 stay labeled.

## What was kept

The object: for one KEY, empty assignment is a different event from unset.
Ordinary `printenv` cannot see a file's `KEY=` once a skip-empty loader
left inherited `/x` in place.

Owned 010: inherited `'/x'`, file empty-assignment `''`, skip_empty `'/x'`
source `inherited`, assign `''` source `file-empty`, process unset.

Duplicate-key policy from FIX is unchanged: `file` / `assign` last
assignment (empty counts); `skip_empty` last non-empty. `KEY=fromfile`
then `KEY=`, inherited `/x` → skip_empty `'fromfile'` source `file`, not
inherited. Last-wins-then-skip is still rejected.

## Change (DESTROYER_envlayers mutation 1–6)

1. **Assignment events are explicit.** `file_n` is the count of file
   assignments for KEY. skip_empty source is `file` when a non-empty file
   assignment exists, `inherited` only when none does. Presence labels:
   file `omitted` / `absent` / `empty-assignment` / `value`.

2. **Declared dotenv subset; refuse the rest.** Strip, `#` comments, BOM,
   optional `export `, spaces around `=`, `KEY=""` / `KEY=''` are empty.
   `export KEY` without `=` is `not an assignment` (rc=1), not key
   `"export KEY"`. `# KEY=secret` is not a key.

3. **Inherited is caller-supplied.** Default inherited is empty, not a
   copy of `os.environ`. `--from-process-env` is opt-in (`source
   process-copy`). `--no-process-env` remains the default. Default mode
   does not make `inherited == process`. `--process NAME=VALUE` injects
   the process column; otherwise process is this CLI `os.environ`.

4. **Presence + source, not only Python `None`/`''`.** Four TSV columns:
   layer, `repr(value)`, presence, source. Display cap 256 + `…`.

5. **One CLI.** `./envlayers` is the program. `envlayers.py` re-exports
   that file (same flags: `--inherited` / `--inherit`). Tests load
   `envlayers`. Duplicate keys, `KEY=""`, `export KEY`, BOM, missing
   file, process empty vs unset, omitted `--file` are tested.

6. **Clean errors kept and extended.** Missing path vs directory vs
   empty file (`absent`) vs omitted `--file` (`omitted`). Empty names
   refused. Invalid UTF-8 still `not utf-8`. Huge values truncated on
   the display path.

## Before → after

Quoted empty `KEY=""` with inherited `/x` (was truthy `'""'`, skip_empty
overwrote inherited):

```
file	''	empty-assignment	text
skip_empty	'/x'	present	inherited
assign	''	empty	file-empty
```

`export KEY=exported` / `# KEY=secret` (was silent wrong keys):

```
# KEY=secret skipped; export binds KEY
file	'exported'	value	text
```

Default `env KEY=live envlayers KEY` (was inherited == process):

```
inherited	None	absent	none
process	'live'	present	os.environ
```

## Not faked (leftover)

(1)+(2)+(3) still apply two hardcoded policies (`if v:` vs always assign)
to a caller-labeled inherited map and a file. Process without `--process`
is this CLI. Grounder forbids attach. There is no third loader, no
"match this printenv snapshot" beyond `--process` injection, no
observation of what another process's loader did.

If a later destroyer still sees only `printenv` of caller-labeled layers
and wants a third policy or a live attach, they should **KILL**. Do not
add envprobe. Do not pretend this table discovered which merge a
third-party tool used.

- FIFO `--file` still blocks in `open()`.
- Null bytes in a UTF-8 file are refused (`nul in assignment`).
- POSIX key names only; `FOO=BAR` as a query is `bad key`.
- `envlayers.py` exists only as a fold onto `./envlayers`.
