# DESTROYER envlayers

Date: 2026-09-02

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/envlayers`

Worktree (optional, already diverged): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers/`

Origin claim: one KEY across inherited / file / skip_empty / assign / process, because empty assignment is not unset.

Happy path is real. Unit tests (9/9) pass. Specimen-010 `KEY=` vs inherited `/x` is reproduced. That is not enough. The implementation is a naive `partition("=")` calculator, and the primitive is still two hardcoded specimen loaders plus `os.environ.get` of *this* CLI process.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-envlayers/envlayers
PYF=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-envlayers-envlayers/envlayers/envlayers.py
```

---

## What still works

Empty unquoted `KEY=` is not treated as absent. Skip-empty keeps inherited `/x`. Assign stores `''`. Process `None` vs `''` is distinguished when `--no-process-env` is used.

```bash
printf 'KEY=\nOTHER=2\n' > /tmp/el.env
env -u KEY python3 "$CLI" --no-process-env --inherited KEY=/x --inherited OTHER=1 --file /tmp/el.env KEY
```

```text
key	KEY
inherited	'/x'
file	''
skip_empty	'/x'
assign	''
process	None
```

```bash
env -u KEY python3 "$CLI" --no-process-env --file /dev/null KEY   # process	None
env KEY= python3 "$CLI" --no-process-env --file /dev/null KEY     # process	''
```

That is the whole useful delta. Attacks below break the claim around it, or show the primitive cannot grow.

---

## Implementation

### 1. Duplicate keys: file layer last-wins empty; skip_empty keeps an earlier file value

Archive `parse_assignments` last-wins. Archive `load_skip_empty` walks lines and *skips* empty, so it never unsets a previous non-empty file assignment. The table then shows a skip_empty value that is neither inherited nor the file layer.

```bash
printf 'KEY=fromfile\nKEY=\n' > /tmp/dup.env
env -u KEY python3 "$CLI" --no-process-env --inherited KEY=/x --file /tmp/dup.env KEY
```

```text
inherited	'/x'
file	''
skip_empty	'fromfile'
assign	''
```

`file` says empty assignment. `skip_empty` says `'fromfile'`. A reader of the README ("skip-empty keeps the inherited value") will look at inherited `/x` and be wrong.

Worktree `envlayers.py` already disagrees: it last-wins the file map *first*, then skip-empty, so skip_empty is `/x` with source `inherited`.

```bash
env -u KEY python3 "$PYF" KEY --file /tmp/dup.env --inherit KEY=/x
```

```text
file         empty-assignment
skip_empty   present            /x               inherited
assign       empty              ·                file-empty
```

Same input, two "envlayers" in one lineage, two answers. Tests never assign KEY twice, so they cannot see it. This is a spec hole, not a typo.

### 2. "dotenv-style" is a lie: quoted empty, export, comments, BOM, whitespace all exit 0

README: "dotenv-style file (`KEY=` is empty, absent key is unset)". Real dotenv empty is often `KEY=""`. Archive treats that as a *truthy* two-character value, so skip_empty overwrites inherited instead of keeping `/x`.

```bash
printf 'KEY=""\n' > /tmp/q.env
env -u KEY python3 "$CLI" --no-process-env --inherited KEY=/x --file /tmp/q.env KEY
```

```text
file	'""'
skip_empty	'""'
assign	'""'
```

The empty-vs-unset thesis fails on the common spelling of empty. Worktree `envlayers.py` also reports `file=value` `""` and `policies_disagree false`.

Other silent misses (rc=0, KEY absent):

| input | what happens |
| --- | --- |
| `export KEY=value` | key becomes `"export KEY"`; query `KEY` → all None; query `export KEY` → `'value'` |
| `# KEY=secret` | key becomes `"# KEY"`; query `KEY` → None; query `# KEY` → `'secret'` |
| UTF-8 BOM + `KEY=` | key is `"\ufeffKEY"`; query `KEY` → file None (looks unset) |
| `\tKEY=tabbed` | key is `"\tKEY"`; query `KEY` → None |
| `KEY = value` | key is `"KEY "` (trailing space on the name); query `KEY` → None |

```bash
printf '# KEY=secret\nexport KEY=exported\n' > /tmp/c.env
python3 "$CLI" --no-process-env --file /tmp/c.env KEY            # file None
python3 "$CLI" --no-process-env --file /tmp/c.env "# KEY"        # file 'secret'
python3 "$CLI" --no-process-env --file /tmp/c.env "export KEY"   # file 'exported'
```

Worktree `envlayers.py` strips and skips `#`, so tab-indented `KEY` works there and comments do not become keys. Another silent dialect split.

Whitespace-only `KEY= ` (space before newline): archive skip_empty treats `" "` as truthy and *overwrites* inherited; `envlayers.py` strips the line to `KEY=` and calls it empty-assignment. Same file, opposite empty-vs-unset answer.

### 3. Malformed bytes: uncaught UnicodeDecodeError, exit 1 traceback

Missing file is a clean `envlayers: [Errno 2] ...` (rc=1). Invalid UTF-8 is not OSError, so it dumps a traceback.

```bash
printf 'KEY=\xff\n' > /tmp/bad.env
python3 "$CLI" --no-process-env --file /tmp/bad.env KEY ; echo rc=$?
```

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 4
rc=1
```

Binary garbage (`bytes(range(256))`) same crash. Null bytes in a UTF-8 file are accepted (`file 'foo\x00bar'`), which is not a valid env value.

### 4. Missing file vs empty file vs omitted `--file` vs no KEY

| case | rc | file layer |
| --- | --- | --- |
| `--file` path missing | 1 | (stderr only) |
| `--file` is a directory | 1, `Is a directory` | |
| empty file | 0 | `None` |
| omitted `--file` | 0 | `None` |
| no KEY positional | 2 argparse | |
| empty KEY `""` with file line `=emptykey` | 0 | binds the empty name |

Empty file and forgotten `--file` are indistinguishable. Worktree `envlayers.py` at least requires `--file` (missing → rc=2 `"file not found"`, including when the path is a directory).

`--inherited =` (empty name) is accepted by the archive CLI (rc=0). `envlayers.py` refuses (`empty key in '='`, rc=1).

### 5. Process empty vs unset works; default inherited does not

Process distinction is correct *if* you pass `--no-process-env`. Default `build_inherited(..., from_process=True)` copies `os.environ`, so `inherited` and `process` are the same column unless an overlay is applied.

```bash
python3 "$CLI" PATH
# inherited == process  (observed True; inherited repr length 1099 on this host)
```

Without `--no-process-env`, `env KEY= python3 "$CLI" --file f.env KEY` shows inherited `''` and process `''`. The tool's default mode hides the layer split it exists to show. `--no-process-env` is the real interface; the default is a footgun.

`process` is always *this* CLI's `os.environ`. It cannot answer "what did the loader in that other process see?" CANDIDATE.md already concedes this. Then the column is a getenv of the debugger, not a layer of the specimen.

### 6. Huge lines: survives, dumps the value three times

5 MB `KEY=HHH...` returns rc=0 in ~0.06s and writes ~15 MB stdout (`file`, `skip_empty`, `assign` each repr the payload). No cap. A FIFO `--file` with no writer blocks in `open()` until timeout (observed 2s test timeout). Neither is fatal; both are "CLI as pipe component" failures.

### 7. KEY names with `=`

Grammar is first-`=` partition. A key containing `=` cannot exist in file or `--inherited`. Querying one is a silent miss of the actual line.

```bash
printf 'FOO=BAR=baz\n' > /tmp/eq.env
python3 "$CLI" --no-process-env --file /tmp/eq.env 'FOO=BAR'   # all None
python3 "$CLI" --no-process-env --file /tmp/eq.env FOO         # file 'BAR=baz'
python3 "$CLI" --no-process-env --inherited 'FOO=BAR=baz' --file /dev/null FOO
# inherited 'BAR=baz'
```

POSIX env names cannot contain `=`, so process-layer keys are fine. File/overlay identity is still first-equals, and the CLI will happily inspect a KEY that the parser can never produce.

### 8. Pipes

TSV of Python `repr` is actually parse-stable: tabs/newlines inside values become `\t`/`\n` in the field, so `cut -f2` does not split rows. Cost: every consumer must `ast.literal_eval` the field. `cut -f2` on the happy path is `KEY`, `'/x'`, `''`, `'/x'`, `''`, `None` — quoted, not shell values. `grep /x` matches because `'/x'` contains `/x`. Fine for humans; hostile as a Unix filter. Worktree `envlayers.py` is a space-padded table (worse for pipes) and is what worktree `demo.sh` / `README.md` now advertise.

---

## Primitive

Reality-stripped operation: parse `K=V` lines, merge with `if v:` vs `always assign`, print `os.environ.get` of the current process.

Nearest ordinary workflow: read `specimens/specimen-010/files/loader.py` (the two functions *are* that file) and `printenv`. Observable capability lost if envlayers vanishes: none that a five-line Python snippet does not already have. It does not attach, does not name which policy a third-party tool used, does not parse dotenv, does not log per-assignment events.

That is why this is not KILL: the *question* (empty assignment vs unset, and which merge rule won) is a real debugging object. The current embodiment is a specimen replay that pretends to be a layer oracle.

Hardcoded policies are the ceiling. There is no way to add a third loader, a last-wins-then-skip policy, or "match this `printenv` snapshot" without changing the object. Duplicate-key behavior is unspecified and the lineage already forked it. Default inherited=copy of process env collapses two of the five columns. `process` is the wrong process. "dotenv-style" in the README is unsupported certainty: quoted empty, `export`, comments, BOM, and `KEY = v` all exit 0 with the wrong identity.

Worktree split is evidence, not a fix:

- harvested `envlayers`: sequential skip_empty, no strip, no comments, optional `--file`, `--inherited`, TSV `repr`, inherited defaults from `os.environ`
- worktree `envlayers.py`: last-wins then skip, strip, skip `#`, required `--file`, `--inherit`, padded table + `policies_disagree`, inherited is caller-only
- worktree tests still import `envlayers` (the first one). `selfcheck.py` exercises the second. Two CLIs, two parsers, two outputs, one name.

---

## Mutation (what must change)

Keep the object: for one KEY, empty assignment is a different event from unset.

Do not keep a calculator that only replays specimen-010's two functions.

1. **Specify assignment events.** Duplicate `KEY=fromfile` then `KEY=` must be an explicit event (count, last empty overlays prior file value, skip_empty result, whether skip kept inherited vs an earlier file line). Pick last-wins-then-skip *or* sequential-skip and kill the other. Today both exist.
2. **Declare a file grammar and refuse the rest.** Either parse a dotenv subset (`export`, quotes so `KEY=""` is empty, comments, strip, BOM) or reject those lines with rc≠0. Silent wrong-key (`export KEY`, `# KEY`, `\ufeffKEY`) is the current product.
3. **Inherited is caller-supplied.** Do not clone `os.environ` by default. Process env is an injected map or omitted. Default mode must not make `inherited == process`.
4. **Presence labels, not only Python `None`/`''`.** File `absent` vs `empty-assignment` vs `value` (worktree table has this; archive TSV does not). Source of skip_empty must not claim inherited when the value came from an earlier file line.
5. **One CLI.** Delete or fold `envlayers.py` vs `envlayers`. Same flags, same parser, same tests. Tests must include duplicate keys, `KEY=""`, `export KEY`, BOM, missing file, process empty vs unset, omitted `--file`.
6. **Clean errors.** Catch `UnicodeDecodeError`. Distinguish missing path vs directory vs empty file vs omitted `--file`. Refuse empty names. Cap huge values in the display path.

If the mutation cannot do (1)+(2)+(3), the object is still `loader.py` with extra print, and a later destroyer should KILL.

---

MUTATE
