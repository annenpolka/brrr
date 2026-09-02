# DESTROYER poslayer 2

Date: 2026-09-02 15:54 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0408
Worker: destroyer-poslayer-2

Target (archive; mutate never queued):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/poslayer`

sha256 `0a47eaf09c2e4e9e939cb2bfe7c32d6517d431f52c2524323bdfa2f1db7657c0` (`poslayer`, 7142 bytes, 224 lines). Same digest as `DESTROYER_poslayer.md`. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-poslayer-poslayer/poslayer/poslayer` is **byte-identical** (`cmp` rc=0). HEAD `ef3e62b447345a55cc9e53077c1a3be11eed61ad` (`Record poslayer empirical transcript from specimen-019 demos.`), parent `413d0cc` (`Dogfood poslayer: leftover enters only via substitution.`), branch `specimen-hdd/candidate-poslayer-poslayer`. Parent `main` is `432f954c0dce09f1b72084a66075051d884cba61`; `git ls-tree HEAD poslayer` empty. HEAD is not an ancestor of `main`. Host Python 3.14.5. `command -v tox` empty; tox was not invoked. unittest 13/13 (`Ran 13 tests in 0.192s` `OK`). `./demo.sh` live log byte-identical to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0). No merge onto `main`. Archive was not edited. No `MUTATE.md`. No `mutate-poslayer` job in `jobs.jsonl`.

Origin (`CANDIDATE.md` / harvest `hdd-ctr019` / specimen-019): name which layer expanded a template token versus leftover CLI args that never entered it. Kind: USEFUL_COMPOSITION. Embodiment: two caller strings plus leftover plus a token. tox.ini / `-x` / child argv are not observed.

First destroyer (`DESTROYER_poslayer.md`) **MUTATE**: `expanded`/`literal` is “token still an argv word”; `entered` is substring in the template; `ran_against` is `argv[-1]`; `--exit` is a sticker; `-` is empty and a word; join-then-split is not leftover identity. Kill condition for a later destroyer: if mutation cannot do slot-fill-or-refuse (1) + entered-is-occupying-the-slot (2) + exit-observed-or-omitted (4), the object is still `override_subst.py` with extra print, **KILL**. First MUTATE is not protection. Job kill condition: Honor KILL if THIN_WRAPPER of caller-labeled position/layer rows.

This candidate is a **THIN_WRAPPER of caller-labeled position/layer rows**. The two “layers” are `--file-template` / `--override` strings the caller already typed. Position is `override_argv[-1]`. Independent replica (`destroyers/_poslayer2_scratch/replica.py`; does not import poslayer) is **byte-identical** to CLI stdout+rc on **45/45** host cases. Owned harvest stdout is byte-identical to `printf` of the ten TSV rows (**10/10**, sha256 `b67870f3b9458af42449e49198705795aa87d8c1353643c0fc0734cc343fa6a2`). Owned fixture `override_subst.py` already prints `file_argv` / `override_argv` / `cli_leftover` / `override_exit 0` / `override_ran_against {posargs}`. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/poslayer
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-poslayer/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-poslayer-poslayer/poslayer/poslayer
S019=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-019/files/override_subst.py
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run tox / pytest. Do not grow a tox.ini / `-x` / quoting parser to escape THIN_WRAPPER. Do not send leftover-posargs theater back to R1.

---

## What still works

The owned fixture, unseen `{packages}` leftover `pkg`, coincidental override word `tests`, `--subst-override` on the same spelling, and any other pair of strings whose only difference is “replace `{token}` with leftover joined by space, then split” versus “split with no replace”, when leftover items are ordinary non-empty words that are not the token and do not contain whitespace.

```bash
python3 "$CLI" --file-template 'pytest {posargs}' -- tests src
echo rc=$?
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

`cmp` of CLI stdout vs `printf` of those ten rows: **identical**, sha256 `b67870f3b9458af42449e49198705795aa87d8c1353643c0fc0734cc343fa6a2`. 10/10 CLI runs match. `--file` fixture is the same bytes. `--subst-override` is both layers `expanded`, `entered file override`, `missed -`, `ran_against src`, `silent no`. Coincidental `pytest tests {posargs}` leftover `tests src` is `in_override tests` and still `missed tests src`. Unseen `{packages}` leftover `pkg` is the same labels with the braces renamed. Unicode leftover `テスト` and token `{引数}` work. Missing path / directory / empty `--file` / empty `--file-template` / both flags: clean `poslayer:` errors (rc 1 or 2). unittest 13/13. Demos identical.

That is the first MUTATE surface. It is also two caller strings plus leftover, with `expanded`/`literal` as token membership and `ran_against` as last word. `demo.sh` already prints the three caller strings before the CLI:

```text
== nearest existing operation (print argv and the template) ==
file template: pytest {posargs}
override template: pytest {posargs}
leftover: tests src
```

Host `python3 "$FIX/override_subst.py"` (byte-identical run vs `$S019` except one leading newline on the specimen copy) already prints:

```text
file_argv ['pytest', 'tests', 'src']
override_argv ['pytest', '{posargs}']
cli_leftover ['tests', 'src']
override_exit 0
override_ran_against {posargs}
```

The CLI will not parse that log. It reprints the same join as TSV.

---

## Implementation

Load-bearing body of `inspect()`:

```python
file_argv = to_argv(subst(file_template, leftover, token))
if subst_override:
    override_argv = to_argv(subst(override_template, leftover, token))
else:
    override_argv = to_argv(override_template)
file_state = token_state(file_template, file_argv, token)
override_state = token_state(override_template, override_argv, token)
entered: list[str] = []
if token in file_template:
    entered.append("file")
override_took_leftover = subst_override and token in override_template
if override_took_leftover:
    entered.append("override")
missed = [] if override_took_leftover else list(leftover)
silent = override_state == "literal" and exit_code == 0
# ran_against = override_argv[-1]
```

`subst` is `template.replace(token, " ".join(leftover))`. `to_argv` is `command.split()`. `token_state` is `token in argv` → `literal`, else `token in template` → `expanded`, else `absent`. `inspect.co_names` is `('to_argv', 'subst', 'token_state', 'append', 'list', 'leftover_present')`. `subst.co_names` is `('replace', 'join')`. `to_argv.co_names` is `('split',)`. `token_state.co_names` is `()`. Source contains no `tox`, `pytest`, `subprocess`, `shlex`, `Popen`. `--exit` is `argparse` `type=int` default 0. `main` returns 0 after a successful format.

The caller already labeled the layers (`--file-template` / `--override`), the leftover vector, the token, the exit sticker, and whether the override layer should run the same replace.

---

## 1. THIN_WRAPPER of caller-labeled position/layer rows

Replica of the TSV (does not import poslayer):

```python
file_argv = template.replace(token, " ".join(leftover)).split()
override_argv = (override.replace(token, " ".join(leftover)).split()
                 if subst_override else override.split())
# file/override state: token in argv → literal; token in template → expanded
# entered: "file" if token in file_template; "override" if subst_override and token in override
# missed: leftover unless override substitution ran
# ran_against: override_argv[-1]          # position
# silent: override_state == "literal" and exit_sticker == 0
```

45/45 host cases: stdout byte-identical, rc identical (owned 019, unseen `{packages}`, coincidental `tests`, `--subst-override`, leftover-is-token, leftover-is-token + subst, quoted `'{posargs}'`, glued `{posargs}-extra`, trailing `--tb=short` ± subst, `--exit 1`, `--exit -1`, empty leftover, leftover `-`, override word `-`, space in one leftover item, override `pytest` ± subst, unicode leftover, unicode token, empty `--token`, substring `test`, partial `{pos`, double token, `not{token}yes`, whitespace-only template, tab-only template, empty override, leftover `-` + subst, leftover `-k test_foo`, quoted leftover item, `café`, explicit same-spelling override, override plus flag, token with a space, duplicate leftover word, leftover `pytest src` coincidental count, both layers absent, `--exit 0`, `--file` 019, `--file` unseen, `--file` no newline, `--file` two newlines, `--file` CRLF).

Owned harvest `printf` of the ten rows matches CLI stdout **10/10**.

Nearest ordinary workflow: the replica above, or:

```bash
python3 "$FIX/override_subst.py"
printf '%s\n' 'file template: pytest {posargs}' 'override template: pytest {posargs}' 'leftover: tests src'
```

`echo $?` of a real tox/pytest child still leaves that join as a hand comparison — but this CLI does not run a child. The harvest question (file expanded, override kept `{posargs}` literal, leftover `tests src` unused, exit 0) is real. This embodiment asks it of two strings plus leftover the caller already typed, then names the last override word as position and the two strings as layers.

---

## 2. MUTATE leftovers (1)+(2)+(4) still hold; mutation never landed

First-destroyer must-change (1): `expanded` means the slot was filled, or refuse. Still `token in argv` vs `token in template`. Leftover that *is* the token is `file literal` + `entered file` + `silent yes` (the hole filled with the hole). `--subst-override` leftover `{posargs}` is both layers `literal`, `entered file override`, `missed -`, `silent yes`. Quoted `'{posargs}'` is `override expanded` without `--subst-override`. Glued `{posargs}-extra` leftover `tests` is both layers `expanded`, `ran_against {posargs}-extra`, `silent no`. Empty `--token` is Python `str.replace("", leftover)` between every character, rc=0, `file expanded X p X y X t X e X s X t X X { X p X o X s X a X r X g X s X } X`. Two `{token}` slots both get the join. Substring `--token test` on `pytest tests` leftover `FOO` is `file expanded pyFOO FOOs`.

First-destroyer must-change (2): `entered` is leftover occupying that layer's slot. Still `token in file_template`. Empty leftover is `entered file`, `leftover -`, `silent yes`. `not{posargs}yes` leftover `X` is `file expanded` argv `notXyes`, `entered file`. The leftover never occupied an argv word.

First-destroyer must-change (4): `exit` is observed or omitted; a sticker must not flip `silent`. Still `--exit` argparse int. `--exit 1` on owned 019:

```text
override	literal	pytest	{posargs}
missed	tests	src
exit	1
silent	no
rc=0
```

The harvest diagnosis is gone. `--exit -1` is `silent no` too. Default `--exit 0` makes every literal override `silent yes`, including empty leftover (nothing was missed) and leftover `{posargs}` (substitution produced the token). `silent yes` and `silent no` are both tool rc=0. pytest against a directory named `{posargs}` is not observed.

Must-change (3) `ran_against` is still `argv[-1]`. Trailing `--tb=short`:

```text
override	literal	pytest	{posargs}	--tb=short
ran_against	--tb=short
silent	yes
```

The literal token is sitting in the argv. The column names `--tb=short`. `--subst-override` on the same template is `ran_against --tb=short` too — leftover `src` is not last. Empty override argv is `ran_against -`. `--subst-override` leftover `-` is also `ran_against -`. Same cell, two meanings.

Must-change (5) sentinel: leftover `[]` and leftover `['-']` both print `leftover	-` / `missed	-` / `in_override	-`. File argv differs (`pytest` vs `pytest -`); the leftover/missed/in_override rows do not. Join-then-split still splits `'tests src'` into two argv words. Tabs/newlines in leftover still wreck the TSV.

Must-change (6) `--file -` is still `file not found: -`. `except ValueError` still wins over `UnicodeDecodeError`; `file_error(..., UnicodeDecodeError)` `not utf-8` is still dead.

Must-change (7) leftover-as-append: `--override pytest -- tests src` is still `override absent pytest`, `missed tests src`, `ran_against pytest`. `--subst-override` on that override is identical. Token not in override template; leftover never appends after `--`. CANDIDATE.md listed this. Unimplemented.

Bytes unchanged. No mutate job. Kill condition `still override_subst.py with extra print` holds.

Errors (non-fatal to the classification): no args rc=2; missing path rc=1 `file not found`; empty `--file-template` rc=1; both `--file` flags rc=2; leftover `-k` without `--` argparse rc=2 `unrecognized arguments: -k`. `--file -` is not stdin.

---

## Primitive

Reality-stripped operation: `template.replace(token, " ".join(leftover)).split()` versus `override.split()`, then `token in argv` vs `token in template`, stamp caller `--exit`, `silent = (override_state == "literal" and exit == 0)`, print last argv word as `ran_against`. Layer names (`file` / `override` / `entered`) are labels of the two caller strings. Position (`ran_against`) is `argv[-1]`.

Nearest: the replica in §1, or `override_subst.py`, or `printf` of both templates plus leftover. Observable capability lost if poslayer vanishes: **none**. The named join the first destroyer kept is formatting of caller-labeled position/layer rows (`file expanded` / `override literal` / `missed` leftover / `silent yes` / last word). `demo.sh` already prints the three strings.

Ceiling, now measured:

- `expanded` / `literal` = token still an exact argv word; leftover-is-token, quotes, glue, empty token, substring, and spaced tokens all lie
- `entered` = substring in the template string, including empty leftover and `not{token}yes`
- `ran_against` = `argv[-1]`; flags after `{posargs}` steal the tox diagnosis
- `silent` / `exit` are not observed; `--exit 1` hides `silent yes`; tool rc=0 either way
- `missed` = all leftover unless `--subst-override` and token in override template; leftover never appends after `--`
- `-` is empty and a word on leftover / missed / in_override
- `{packages}` is `{posargs}` with the braces renamed
- `file_error` `not utf-8` is dead under `except ValueError`
- mutation of (1)+(2)+(4) never queued; bytes identical to first MUTATE

Honor KILL. Dreamer ancestry is not protection. First-destroyer MUTATE is not protection once leftover+rc is shown to be caller-labeled position/layer rows. Constitution: a THIN_WRAPPER does not gain a tox parser to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Do not merge onto `main`. Do not run tox. Do not grow a quoting grammar / child-process tracer / tox.ini reader. Archive stays under `lineages/candidate-poslayer/`. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/candidate-poslayer-poslayer/`. Reimpl of this primitive is not a survivor.

KILL
