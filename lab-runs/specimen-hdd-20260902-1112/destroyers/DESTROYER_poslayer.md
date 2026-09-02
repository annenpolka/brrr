# DESTROYER poslayer

Date: 2026-09-02 13:17 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/poslayer`

Worktree (byte-identical, sha256 `0a47eaf09c2e4e9e939cb2bfe7c32d6517d431f52c2524323bdfa2f1db7657c0`, 7142 bytes): `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-poslayer-poslayer/poslayer/poslayer`

Origin claim: name which layer expanded a template token versus leftover CLI args that never entered it. File-backed `pytest {posargs}` plus leftover `tests src` expands; a CLI override of the same spelling keeps `{posargs}` as an argv element; leftover stays beside it; exit 0 still looks like the intended command ran.

Happy path is real. Unit tests (13/13) pass. Specimen-019 `file_argv ['pytest', 'tests', 'src']` vs `override_argv ['pytest', '{posargs}']` is reproduced as `file expanded` / `override literal` / `missed tests src` / `silent yes`. That is not enough. The implementation is `str.replace` plus `str.split` plus a caller sticker named `--exit`, and `silent` is that sticker times “token still an argv word”.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/poslayer
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/fixtures
S019=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-019/files/override_subst.py
```

`cmp "$FIX/override_subst.py" "$S019"` differs by one leading newline on the specimen copy. Same `subst` / `split` functions. Host: Python 3, no tox installed in these runs. No merge onto `main`. This object is the expansion-layer vs leftover-unused join, not a tox runner.

---

## What still works

The owned fixture, and any other pair of strings whose *only* difference is “replace `{token}` with leftover joined by space, then split” versus “split with no replace”, when leftover items are ordinary non-empty words that are not the token and do not contain whitespace.

```bash
python3 "$CLI" --file-template 'pytest {posargs}' -- tests src
python3 "$CLI" --file "$FIX/019-file.txt" -- tests src
```

```text
token	{posargs}
leftover	tests	src
file	expanded	pytest	tests	src
override	literal	pytest	{posargs}
entered	file
in_override	-
missed	tests	src
ran_against	{posargs}
exit	0
silent	yes
rc=0
```

`--subst-override` on the same spelling is both layers `expanded`, `entered file override`, `missed -`, `silent no`, `ran_against src`. Coincidental override word `pytest tests {posargs}` leftover `tests src` is `in_override tests` and still `missed tests src` — leftover membership is not entry. Unicode leftover `テスト` and token `{引数}` work. Missing path / directory / empty `--file` / empty `--file-template` / both flags are clean `poslayer:` errors (rc 1 or 2). Symlink, space in path, and `/dev/stdin` as `--file` work.

That is the whole useful delta. Attacks below break the expansion-vs-literal claim around it, or show the primitive cannot see a normal tox override.

---

## Implementation

### 1. `expanded` / `literal` is “token still an argv word”, not “substitution ran”

`token_state` is:

```text
token in argv        → literal
token in template    → expanded
else                 → absent
```

`argv` membership is exact. `template` membership is a substring. Substitution is `template.replace(token, " ".join(leftover))`. Those three predicates disagree.

Leftover *is* the token. Substitution ran. File argv is still `pytest {posargs}`:

```bash
python3 "$CLI" --file-template 'pytest {posargs}' -- '{posargs}'
```

```text
file	literal	pytest	{posargs}
override	literal	pytest	{posargs}
entered	file
in_override	{posargs}
missed	{posargs}
silent	yes
```

`file literal` and `entered file` on the same report. The hole was filled with the hole.

`--subst-override` leftover `{posargs}` is worse: both layers `literal`, `entered file override`, `missed -`, `silent yes`. The repaired pass still prints the harvest lie.

Quoted token, no substitution:

```bash
python3 "$CLI" --file-template 'pytest {posargs}' --override "pytest '{posargs}'" -- tests src
```

```text
override	expanded	pytest	'{posargs}'
ran_against	'{posargs}'
silent	no
```

`'{posargs}'` is not the argv word `{posargs}`, so the override is `expanded` without `--subst-override`. Glued token `pytest {posargs}-extra` leftover `tests` is the same lie: both layers `expanded`, `ran_against {posargs}-extra`, `silent no`. NUL suffix `{posargs}\x00` in a file is `override expanded` / `ran_against {posargs}\x00` / `silent no`. Token with a space (`--token 'POS ARGS'` on `pytest POS ARGS`) splits into `POS` and `ARGS`, so the override is `expanded` and `ran_against ARGS`.

Substring replace is not a slot:

```bash
python3 "$CLI" --file-template 'pytest tests' --token test -- FOO
# file	expanded	pyFOO	FOOs
python3 "$CLI" --file-template 'pytest {posargs}' --token '{pos' -- X
# file	expanded	pytest	Xargs}
python3 "$CLI" --file-template 'pytest {posargs}' --token '' -- X
# file	expanded	X p X y X t X e X s X t X X { X p X o X s X a X r X g X s X } X
```

Empty `--token` is Python `str.replace("", leftover)` between every character. rc=0.

Double token `pytest {posargs} {posargs}` leftover `a b` becomes `pytest a b a b`. Both slots get the join. Not per-slot leftover.

### 2. `entered` is “token substring in the template string”

```python
if token in file_template:
    entered.append("file")
override_took_leftover = subst_override and token in override_template
```

Empty leftover still `entered file`. Template `pytest not{posargs}yes` leftover `X` is `file expanded` argv `notXyes`, `entered file`. The leftover never occupied an argv word.

`entered` does not mean leftover appears in that layer's argv. `in_override` is the membership column; `entered` is a string find.

### 3. `ran_against` is the last override argv word

Specimen-019 ends with `{posargs}`, so last-element coincidence looks like the tox bug (`pytest` ran against a directory named `{posargs}`). A trailing flag kills it:

```bash
python3 "$CLI" --file-template 'pytest {posargs} --tb=short' -- tests src
```

```text
override	literal	pytest	{posargs}	--tb=short
ran_against	--tb=short
silent	yes
```

The literal token is sitting in the argv. The column names `--tb=short`. `--subst-override` on the same template is `ran_against --tb=short` too — leftover `src` is not last. Multiline `--file` (`pytest {posargs}\n--tb=short\n`) is the same last-word steal after `str.split()`.

Empty override argv is `ran_against -`. `--subst-override` leftover `-` is also `ran_against -`. Same cell, two meanings.

### 4. `--exit` is a sticker. `silent` is that sticker times `literal`

`--exit` is an int flag, default 0. It is not tox's status and not pytest's status unless the caller copies it in.

```bash
python3 "$CLI" --file-template 'pytest {posargs}' --exit 1 -- tests src
```

```text
override	literal	pytest	{posargs}
missed	tests	src
exit	1
silent	no
rc=0
```

The harvest diagnosis is gone. `--exit -1` is `silent no` too. Default `--exit 0` makes every literal override `silent yes`, including empty leftover (nothing was missed) and leftover `{posargs}` (substitution produced the token).

`silent yes` and `silent no` are both tool rc=0. Fine as a printer; hostile as a pipe predicate. pytest against a directory named `{posargs}` is not observed.

### 5. `-` is the empty sentinel and a legal leftover word

`format_list` prints `-` when a list is empty. Leftover `['-']` is a one-element list, so it also prints `-`.

```bash
python3 "$CLI" --file-template 'pytest {posargs}'          # leftover	-
python3 "$CLI" --file-template 'pytest {posargs}' -- -    # leftover	-
python3 "$CLI" --file-template 'pytest {posargs}' --override 'pytest - {posargs}' -- -
# leftover	-
# in_override	-     # the word is present
# missed	-
```

`leftover`, `missed`, and `in_override` rows for leftover `['-']` are byte-identical to leftover `[]` on those three names. `in_override -` means both “none present” and “the leftover word `-` is present”. `--` is not required: argparse accepts a bare `-` as leftover. `--file -` is `file not found: -`. `/dev/stdin` works. Two meanings of dash, neither is stdin on `--file`.

Empty leftover *item* (`--` then `""` then `tests`) is `leftover\t\ttests` (empty field) and `" ".join` then `split` drops it, so file argv is `pytest tests`. Two empty items: `leftover\t\t\tx`.

### 6. Join-then-split is not leftover identity

Leftover is a list. Substitution joins with a space, then splits on any whitespace. One leftover item with a space is two argv words:

```bash
python3 "$CLI" --file-template 'pytest {posargs}' -- 'tests src'
# leftover	tests src          (one cell)
# file	expanded	pytest	tests	src
```

Tab inside one leftover item:

```text
leftover	tests	src          # looks like two leftover words
file	expanded	pytest	tests	src
```

`cut -f*` cannot tell leftover-with-tab from leftover `tests` `src`. Newline inside leftover splits the TSV row:

```text
leftover	tests
src
```

Quoted leftover item `"tests src"` becomes file argv `pytest` `"tests` `src"`. Naive `.split()` is documented. It still emits `expanded` as if the leftover list occupied the slot.

### 7. File grammar: one trailing newline, then hope

`--file` strips a single trailing `\n`. Empty file and newline-only file are `empty template` (rc=1). Two newlines remain `\n` after one strip, which is truthy, so rc=0 / `file absent` / `ran_against -`. `/dev/null` is empty-template. Whitespace-only `--file-template '   '` and tab-only `\t` are rc=0 `absent`.

CRLF `pytest {posargs}\r\n` works because `\r` is whitespace after replace. UTF-8 BOM stays on the first argv word (`\ufeffpytest`); query still “works” because `{posargs}` is later. Invalid UTF-8 is not the written `not utf-8: PATH` path: `UnicodeDecodeError` is a `ValueError`, and `except ValueError` runs first, so stderr is the raw codec string:

```text
poslayer: 'utf-8' codec can't decode byte 0xff in position 17: invalid start byte
```

`file_error(..., UnicodeDecodeError)` returns `not utf-8: PATH` and is dead. Latin-1 `café` same ugly rc=1. NUL in a UTF-8 file is accepted (see §1). FIFO `--file` with no writer blocks in `open()` (observed 2s timeout). `--file -` is not stdin.

### 8. Huge inputs, pipes, leftover flags

200_000-char leftover word: rc=0, 600_157 bytes of stdout (`leftover` + `file` argv + `missed` each dump the payload). 200k template the same. No cap.

Leftover `-k test_foo` without `--` is argparse rc=2 `unrecognized arguments: -k`. With `--` it is leftover and `file expanded pytest -k test_foo`. The tox analogue `tox … -- tests src` needs `--` here too; leftover *before* options also works (`poslayer tests src --file-template '…'`), which is the opposite of “leftover is the `--` tail”.

Happy-path TSV is ragged: `leftover` has 3 columns, `file` has 5, `entered` has 2. `cut -f2` is `{posargs}` / `tests` / `expanded` / `literal` / `file` / `-` / `tests` / `{posargs}` / `0` / `yes` — not a value column.

### 9. Unseen `{packages}` is a rename. Append is refused.

```bash
python3 "$CLI" --file-template 'pytest {packages}' --token '{packages}' -- pkg
```

Same labels as leftover `pkg` on `{posargs}`. Transfer was not run.

Override with no token (the `--` forwarding tox actually does when the override command is `pytest`):

```bash
python3 "$CLI" --file-template 'pytest {posargs}' --override pytest -- tests src
# override	absent	pytest
# missed	tests	src
# ran_against	pytest
# silent	no
```

`--subst-override` on that override is identical: token not in override template, leftover still not appended. CANDIDATE.md listed this. Unimplemented. The harvest public grounding is tox-dev/tox#4047 (`tox -x '…=pytest {posargs}' -- tests src` ran pytest against `{posargs}`). This CLI never sees tox.ini, never sees `-x`, never sees a child argv. It labels two strings the caller already typed.

### 10. Empty / weird inputs (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| no args | 2 | `--file or --file-template is required` |
| missing path | 1 | `file not found` |
| directory | 1 | `is a directory` |
| empty file / `\n` only | 1 | `empty template` |
| `\n\n` file | 0 | `absent` |
| `/dev/null` | 1 | empty template |
| `/dev/stdin` | 0 | works |
| `--file -` | 1 | `file not found: -` |
| broken symlink | 1 | `file not found` |
| mode 0 | 1 | `Permission denied` |
| latin-1 / `0xff` | 1 | raw `UnicodeDecodeError`, not `not utf-8` |
| `--exit nope` | 2 | argparse |
| both `--file` flags | 2 | clean |
| FIFO no writer | hang | killed at 2s |
| leftover `-` | 0 | collides with empty sentinel |
| empty leftover | 0 | `file expanded pytest`, `silent yes` |

These do not save the state / `silent` / last-word holes.

---

## Primitive

Reality-stripped operation: `template.replace(token, " ".join(leftover)).split()` versus `override.split()`, then `token in argv` vs `token in template`, stamp caller `--exit`, `silent = (override_state == "literal" and exit == 0)`, print last argv word as `ran_against`.

Nearest ordinary workflow: the specimen already ships `files/override_subst.py`, which prints `file_argv`, `override_argv`, `cli_leftover`, `override_exit 0`, `override_ran_against`. `printf` of both templates plus leftover is the same observation. Observable capability lost if poslayer vanishes: the **named join** (`file expanded` vs `override literal` vs `missed` leftover vs `silent yes`) as one TSV. That join is real on specimen-019 and on any other unique-word `{token}` that the override did not replace. It is not a tox override auditor, not a quoting parser, not a process tracer (research boundary, honored in prose, violated in output: `exit` and `silent` and `ran_against` read as observed).

That is why this is not KILL: the *question* (CLI override kept `{posargs}` literal, leftover `tests src` never entered that substitution, process still exited 0) is a debugging object `echo $?` will not emit. The current embodiment is a specimen-019 replay that pretends `str.replace` is a slot, that last argv word is what ran, and that a sticker exit is silence.

The ceiling is already written down, and it is too small for the claim:

- `expanded` / `literal` = token still an exact argv word; leftover-is-token, quotes, glue, NUL, and spaced tokens all lie
- `entered` = substring in the template string, including empty leftover and `not{token}yes`
- `ran_against` = `argv[-1]`; flags after `{posargs}` steal the tox diagnosis
- `silent` / `exit` are not observed; `--exit 1` hides `silent yes`
- `missed` = all leftover unless `--subst-override` and token in override template; leftover never appends after `--`
- `-` is empty and a word
- `{packages}` is `{posargs}` with the braces renamed
- `file_error` `not utf-8` is dead under `except ValueError`

Do not grow a tox parser to escape this. Do not merge this join into a general command-line expander. Keep the file-vs-override leftover-entry row.

---

## Mutation (what must change)

Keep the object: for one leftover vector, name which construction expanded the token versus which leftover never entered the override substitution pass, and whether that still looked like success.

Do not keep a join-then-split calculator that only replays `override_subst.py`.

1. **`expanded` means the slot was filled, or refuse.** Substitution is a whole argv word, not `str.replace` of a substring. Leftover that *is* the token is `expanded` (value equals the token), not `literal`. Quoted `'{posargs}'`, glued `{posargs}-extra`, NUL suffix, and tokens containing spaces are `unsupported` (rc≠0) unless a declared quoting grammar consumes them. Empty `--token` is an error. Two `{token}` slots are an error unless the caller picks one.

2. **`entered` is leftover occupying that layer's slot.** Empty leftover is `entered none` / `entered empty-hole`, not `entered file`. `not{token}yes` is not entry. `--subst-override` leftover `{posargs}` must not print `literal` plus `entered override` plus `silent yes`.

3. **`ran_against` is the substituted leftover, or the literal token word.** Trailing `--tb=short` is a different column (`tail`), not a stolen `ran_against`. Empty argv is not the same cell as leftover `-`.

4. **`exit` is observed or omitted.** A caller sticker must not flip `silent`. `silent yes` is only for an actual leftover-miss plus a real (or explicitly sourced) zero. Tool rc=1 on `silent yes`; rc=0 only for a clean expansion or a clean refuse.

5. **Sentinel is not a leftover word.** Empty lists print `none` / `absent`, not `-`. Escape tabs and newlines in cells. Cap huge leftover in the display path. Leftover items containing whitespace stay one cell on both leftover and argv, or refuse.

6. **`--file -` is stdin or an error that says so.** Catch `UnicodeDecodeError` before `ValueError` and use `not utf-8: PATH`. Empty file vs `\n` vs `\n\n` vs whitespace-only: one rule. FIFO timeout.

7. **Dogfood that is not `{packages}`.** Next unseen is leftover-as-append (`override pytest` plus `-- tests src`), a quoted token, leftover equal to the token, or flags after `{posargs}`. The tool must either name the missed leftover / literal slot or refuse with a non-`expanded` / non-`silent yes` row.

If the mutation cannot do (1)+(2)+(4), the object is still `override_subst.py` with extra print, and a later destroyer should KILL.

---

MUTATE
