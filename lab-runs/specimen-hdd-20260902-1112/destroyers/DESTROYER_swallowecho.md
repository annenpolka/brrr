# DESTROYER swallowecho

Date: 2026-09-02 12:50 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-swallowecho/swallowecho`

sha256 `f93554d8a79a5f0018900976b0892da795cd222f03409b32318a9d2b6463a534` (21496 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-swallowecho-swallowecho/swallowecho/swallowecho` is byte-identical. `hidestatus` is a symlink to the same file.

Origin claim: report a compound command whose later success hid an earlier nonzero exit (`|| echo` last-status lie). Name the swallowed command and the resulting step status 0. Specimens `[specimen-043]`. Kind: USEFUL_COMPOSITION.

Happy path is real. Unit tests (24/24) pass. `false || echo ok` names `false` with `step_status 0`. `true && echo ok` is `swallow no`. specimen-043 scheduled bash with `--status 1` names the bazel pipeline, not `[[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]`. That is not enough. Swallow is any `||` success inside a tree whose *final* status happened to be 0, including `if` tests that never become the step status. Modeled `printf` / `set` / `pipefail` claim `ran 0` and then skip the hid. `--status` is the Actions-log observation, not an observation the CLI makes.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-swallowecho/swallowecho
YML=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-043/files/workflows/staleness_check.yml
```

No merge onto `main`. This object is not a PATH install.

---

## What still works

The owned analogue, and any other `||` whose left-hand side is a modeled head (`false`) or a caller-recorded nonzero, whose right-hand side succeeds, and whose **script** status is 0.

```bash
python3 "$CLI" 'false || echo ok'
```

```text
step_status	0
swallow	yes
swallowed	false
swallowed_status	1
hid_by	echo ok
hid_status	0
operator	||
ran	false	1
ran	echo ok	0
rc=0
```

Honesty, same bytes, bash:

```bash
bash -c 'false || echo ok'; echo bash_step_status:$?
# ok
# bash_step_status:0
bash -x -c 'false || echo ok' 2>&1
# + false
# + echo ok
```

`bash -x` plus `$?` still presents status 0. It does not emit the join `swallowed false` / `hid_by echo ok` / `step_status 0`.

Neighbors the tests already own, and that bash agrees with:

| snippet | swallow | step |
| --- | --- | --- |
| `true && echo ok` | no | 0 |
| `false && echo ok` | no | 1 (`skip echo ok left_failed`) |
| `true \|\| echo ok` | no | 0 (`skip echo ok left_succeeded`) |
| `false \|\| false` | no | 1 |
| `false; echo ok` | no | 0 (`;` last-status is not this lie) |
| `false \| echo ok` | no | 0 (pipe last-status is not this lie, no pipefail) |
| `set -e; false \|\| echo ok` | yes | 0 |
| `set -e; false; echo ok` | no | 1 (echo does not run) |
| `false && echo x \|\| echo y` | yes, hid_by `echo y` | 0 |
| `true && false \|\| echo y` | yes, hid_by `echo y` | 0 |
| `if true; then false \|\| echo hid; fi` | yes | 0 |
| `if false; then false \|\| echo hid; fi` | no (then skipped, no `--status` needed) | 0 |
| `if false; then echo x; fi \|\| echo hid` | parse error `expected command, got \|\|` | rc=2 (does **not** attach `\|\|` to `fi`) |

specimen-043 then-body with `--status 1`: swallowed `bazel query 'attr(tags, "staleness_test", //...)' | xargs bazel test $BAZEL_FLAGS`, hid_by the regenerate `echo`. Full folded workflow bash, `--no-process-env --unset COMMIT_TRIGGERED_RUN --unset MAIN_RUN --status 1`: same pipeline, `[[ || ]]` is `ran` status 0, not a swallow site. Unseen `make test || true --status 1`: swallowed `make test`, hid_by `true`. Missing `--status` for bazel is `no status for: …` rc=2, no traceback. `hidestatus` alias same report. Unicode hid_by and `make テスト` work. `--file -`, `/dev/stdin`, symlink, space in path: rc=0.

That is the whole useful delta. Attacks below break the claim that `swallow yes` means the **step** inherited 0 because of `||`, or show the interpreter asserting statuses bash does not.

---

## Implementation

### 1. `if` test `||` is `swallow yes` while the step was already 0 without it

README: `swallow` is `yes` when a `||` success hid a nonzero **and** the step is 0. `eval_andor` records every such site; `analyze` keeps the list iff the **final** list status is 0. An `if` condition is not the step status. Failed `if` tests are 0 with no `else`.

```bash
python3 "$CLI" 'if false || true; then echo then; fi'
```

```text
step_status	0
swallow	yes
swallowed	false
hid_by	true
rc=0
```

```bash
python3 "$CLI" 'if false; then echo then; fi'
```

```text
step_status	0
swallow	no
ran	false	1
rc=0
```

bash: both compounds exit 0; `then` runs only in the first. The `||` changed which **branch** ran. It did not create a green step out of a would-be nonzero step. `if false; then true; fi` is already 0.

Contrast the harvest shape, which the tool **does** get right:

```bash
python3 "$CLI" 'if true; then false || echo hid; fi'
# swallow	yes   hid_by	echo hid
# bash: if true; then false; fi  → status 1
```

The join the specimen needs is "this `||` is why the **step** is 0". Inner boolean rescue is a different object. Today both print `swallow yes`.

### 2. Modeled `printf` and `set` always return 0 — missed swallow vs bash

`run_builtin`: `echo`/`printf`/`set`/`:`/`true` → 0, `false` → 1. No argv is a failure.

```bash
python3 "$CLI" 'printf || echo hid'
```

```text
step_status	0
swallow	no
ran	printf	0
skip	echo hid	left_succeeded
rc=0
```

```bash
bash -c 'printf || echo hid'; echo bash_rc:$?
# printf: usage: printf [-v var] format [arguments]
# hid
# bash_rc:0
```

bash ran the hid. The tool skipped it because `printf` is in `SAFE_HEADS` and cannot fail. Same lie for an invalid `set` option:

```bash
python3 "$CLI" 'set -o unknown || echo hid'
# ran	set -o unknown	0
# skip	echo hid	left_succeeded

bash -c 'set -o unknown || echo hid'
# bash: set: unknown: invalid option name
# hid
```

`ran set -o unknown 0` is unsupported certainty: the interpreter did not run `set`. It returned 0 by construction.

### 3. `set -o pipefail` is `ran 0`, then ignored — missed swallow of the real last-status lie

CANDIDATE.md: pipe last-status is not this primitive; "Honor `set -o pipefail` as a separate pipe-hide" is a suggested mutation. The CLI still **parses** `set -o pipefail` as a successful builtin.

```bash
python3 "$CLI" 'set -o pipefail; false | echo ok || echo hid'
```

```text
step_status	0
swallow	no
ran	set -o pipefail	0
ran	false	1
ran	echo ok	0
skip	echo hid	left_succeeded
rc=0
```

```bash
bash -c 'set -o pipefail; false | echo ok || echo hid'; echo bash_rc:$?
# ok
# hid
# bash_rc:0
```

bash: pipefail makes the pipe 1, `|| echo hid` runs, step 0 — the same last-status lie as `false || echo`, with a pipe on the left. The tool skips the hid. `set -euo pipefail; false | echo ok` is step 0 here and rc 1 in bash.

`run_pipeline` comments "No pipefail" and returns the last command. `set` only looks for `e` in a `-*` flag. `-o pipefail` is swallowed as a successful `set` and forgotten. Printing `ran set -o pipefail 0` is the product claiming an option it does not implement.

specimen-043 is `set -ex` without pipefail, so the owned packet does not hit this. `make test || true` does not either. Transfer onto any `set -o pipefail; cmd | cmd || echo` does.

### 4. Two swallows, one named — `swallows[-1]`

```bash
python3 "$CLI" 'false || echo a; false || echo b'
```

```text
swallow	yes
swallowed	false
hid_by	echo b
ran	false	1
ran	echo a	0
ran	false	1
ran	echo b	0
```

```bash
python3 "$CLI" --status 1 --status 1 'make a || echo x; make b || echo y'
```

```text
swallow	yes
swallowed	make b
hid_by	echo y
recorded	make a	1
ran	echo x	0
recorded	make b	1
ran	echo y	0
```

The join columns name only the last site. `make a` hid by `echo x` is visible only if a reader reconstructs from `recorded`/`ran`. A CI step with two `|| echo` fallbacks reports one. `operator` is hardcoded `||` even when the chain was `&&` then `||` (`true && false || echo hid` still prints `operator ||`, which is the hid operator, not the chain).

A later bare `false` after a real swallow clears the list (`false || echo a; false` → `swallow no`, step 1). That part matches the "step is 0" rule.

### 5. `--status` is the green-log observation; the CLI does not see the echo

Harvest observation: echo sentence in a **successful** Actions log means the right-hand side ran, therefore the left was nonzero. The CLI never reads a log. The caller must already translate that into `--status 1`.

Lie the other way:

```bash
python3 "$CLI" --status 0 'bazel test //... || echo please'
```

```text
step_status	0
swallow	no
recorded	bazel test //...	0
skip	echo please	left_succeeded
rc=0
```

If the log contains `Please run ./regenerate_stale_files.sh`, this report contradicts the log and still exits 0. Extra `--status` values are silently dropped (`--status 1 --status 2 'false || echo ok'` still swallows `false`; `--status 1 'true || bazel'` skips bazel and ignores 1). `--status -1` and `--status 256` are legal nonzeros (`swallowed_status -1`). `--status 08` is 8.

`--file "$YML"` is not a workflow reader:

```text
swallowecho: parse error: unsupported shell syntax near '{}\njobs:'
rc=2
```

`demo.sh` greps `bash: >`, folds YAML, and passes `--status 1`. The extra name the harvest "discovers" is supplied by that rewrite plus the recorded 1. That is the advertised boundary. It means the CLI is a simulator of a snippet the caller already classified.

### 6. Identity: modeled `false` vs `/usr/bin/false` vs assignment prefix vs `!`

On this host `/usr/bin/false` exists (84k), `/bin/false` does not. `false` is a bash builtin and a `SAFE_HEADS` model (always 1). The path form is an unexecuted pipeline:

```bash
python3 "$CLI" '/usr/bin/false || echo ok'
# swallowecho: no status for: /usr/bin/false
# rc=2
```

`--status 1 '/bin/false || echo ok'` reports swallow yes even though bash here is `/bin/false: No such file or directory` (still a nonzero, accidentally). `command false`, `env false`, `builtin true`, `FOO=1 false`, `! false` are all StatusNeeded. bash: `FOO=1 false || echo ok` prints ok; `! false || echo ok` skips echo (`! false` is 0).

Same command, two identities: the harvest `false` is modeled; the real binary is a recorded status the caller must invent. `false -e` stays modeled (bash `false` ignores args, status 1 — this one matches).

### 7. `[[` expansion: `$FOO$BAR` disagrees with bash; unquoted `${FOO}` is a parse error

`$VAR` expands only for a single identifier-shaped word inside `[[`. Juxtaposition is not expanded; the literal `$FOO$BAR` is non-empty, so `-z` is false:

```bash
python3 "$CLI" --no-process-env '[[ -z $FOO$BAR ]]'
# step_status	1

bash -c 'unset FOO BAR; [[ -z $FOO$BAR ]]; echo bash:$?'
# bash:0
```

Unquoted `${FOO}` never reaches `expand_word`. Tokenizer rejects `{`:

```text
swallowecho: parse error: unsupported shell syntax near '{FOO} ]]'
rc=2
```

Quoted `"${FOO}"` works (braces survive inside quotes, then expand). README: "`$VAR` expands only inside `[[`". `${VAR}` is the same expansion, one quoting away from a parse error. `[[ $FOO == bar ]]` and `[[ -f /tmp ]]` refuse cleanly (in-boundary). `[[ -n 1 || -z 1 && -z 1 ]]` matches bash `[[` (AND tighter than OR). `[ -n 1 ] || [ -z 1 ] && [ -z 1 ]` is LTR-equal in bash (status 1) and is not this dialect (`[` needs `--status`).

Default `[[` env is `os.environ`. Leftover `COMMIT_TRIGGERED_RUN=1 MAIN_RUN=1` in the **analyst** process takes specimen-043's else branch (`swallow no`, `ran echo else`) without `--no-process-env`. Demo/tests remember to unset. The default interface does not.

### 8. `elif` is a command name

```bash
python3 "$CLI" 'if true; then echo a; elif true; then false || echo hid; fi'
# swallowecho: no status for: elif true
# rc=2

python3 "$CLI" 'if false; then echo a; elif true; then false || echo hid; fi'
# swallow	no
# ran	false	1
# rc=0
```

`parse_if` only knows `else`/`fi`. On a true `if`, `elif true` is an unsafe simple command. On a false `if`, the `elif` body sits in the skipped then-list and disappears. A swallow after `elif` is either a missing `--status` or a silent `swallow no`. `while`/`for`/`until`/`eval`/`source`/`time`/`exec`/`(` / `{` / redirections / functions are refusals (rc=2). That is acceptable. Pretending `elif` was parsed is not.

### 9. TSV is not a TSV; swallow yes is CLI rc=0; `--check` does not exist

`hid_by` is a source slice. A tab in the snippet becomes an extra field:

```bash
python3 "$CLI" $'false || echo ok\there'
# hid_by\techo ok\there
# ran\techo ok\there\t0
```

`cut -f2` on `hid_by` is `echo ok`, not the hid command. Quoted `'ok\there'` still embeds a tab in the field. 3000 `true;` then a swallow dumps ~33k of `ran true 0` rows. 100k-byte echo arg dumps ~200k stdout. No cap.

CANDIDATE.md listed `--check` exit 1 on `swallow yes`. It is still absent (`unrecognized arguments: --check`, argparse rc=2). Harvest hit and harvest miss are both CLI rc=0. Fine as a printer; hostile as a pipe predicate. `bash -c 'false || echo ok'` is also 0 — the delta is the named row, not the exit.

BOM before `false` is `no status for: ﻿false` (unsafe head). `false || echo ok#hid` is `empty word near '#hid'` ( `#` after a letter is not a comment and is not a word). `false || echo ok # hid` works.

---

## Primitive

Reality-stripped operation: tokenize a tiny shell (`||` `&&` `|` `;` `if/then/else/fi`, `[[ -z/-n/!/||/&& ]]`), model seven heads, consume `--status` for anything else, record every `||` whose RHS ran and succeeded, print the **last** such site if the script status is 0.

Nearest ordinary workflow: `bash -x` plus `$?` on the analogue; for specimen-043, reading the workflow plus noticing the regenerate sentence in a green log. Observable capability lost if swallowecho vanishes: the **named join** (`swallow yes` + which command + hid_by + step 0) as one TSV. That join is real on `false || echo ok` and on a then-body `bazel … || echo` with an honest recorded 1. It is not a YAML parser, not an Actions runner, not `pipefail` (research boundary, half-honored).

That is why this is not KILL: the *question* (which command's nonzero was hidden so the step is still 0) is a debugging object `bash -x` will not emit. The current embodiment is a specimen-043 replay that treats every inner `||` success under a final 0 as that question, and that believes `--status` plus always-zero builtins.

The ceiling is already written down, and it is too small for the claim:

- `swallow yes` = some `||` in the tree succeeded, including `if` tests that cannot become the step status
- `printf` / `set -o unknown` / `set -o pipefail` print `ran 0` and skip the hid bash would run
- join columns are last-site-only
- `--status` is supplied by the caller who already saw the echo; `--status 0` plus a green log is `swallow no`
- modeled `false` is not `/usr/bin/false` and not `FOO=1 false`
- `$FOO$BAR` inside `[[` is a literal; `${FOO}` unquoted is a parse error
- `elif` is an unsafe command
- YAML workflow is not an input; `demo.sh` already extracted the then-body and the 1

Do not grow a GitHub Actions runner or a Bazel executor to escape this. Do not merge this join into a general shell linter. Keep the last-status-lie row.

---

## Mutation (what must change)

Keep the object: a `||` success that is why the **step** is 0 must name the left-hand command that did not become that status.

Do not keep an interpreter that only replays `false || echo ok` and one recorded bazel pipeline.

1. **Swallow is step-status, not inner boolean rescue.** `if false || true; then echo then; fi` is not this primitive (`swallow no`, or a separate `cond` row). `if true; then false || echo hid; fi` stays `swallow yes`. If the mutation cannot tell those apart, a later destroyer should KILL.

2. **Do not `ran 0` options and builtins you do not implement.** `set -o pipefail` is either modeled (pipe status is fail-if-any, and `false | echo ok || echo hid` is a swallow) or a parse/status refusal, never `ran set -o pipefail 0` plus last-command 0. `printf` with no format, `set -o unknown`: refuse or `--status`, not skip the hid. `echo` always-0 is fine if documented.

3. **Every swallow site is a row.** `false || echo a; false || echo b` names both. Last-wins join columns are the current product. `operator` is the hid site's `||`, not a hardcoded string after the fact — same thing, but do not drop the first site.

4. **`--status` unused is an error.** Extra recorded statuses, and `--status` attached to a skipped RHS, are rc≠0. Negative and `>255` statuses are errors. `--status 0` on `cmd || echo` when the question is "echo appeared in a green log" is a liar row: label `recorded` vs `inferred-from-rhs`, or take a log/trace in which the RHS ran.

5. **`--check` is the default for a predicate, or rc=1 on `swallow yes`.** rc=0 only for `swallow no` with no refuse. CANDIDATE already wrote this. Cap `ran` dumps and `hid_by` length. Escape tabs/newlines in TSV fields.

6. **`[[` expansion is bash-small or refused.** `$FOO$BAR` expands or the test is `unsupported [[`. Unquoted `${FOO}` is the same as `$FOO`, not `unsupported {`. Default `[[` env is empty; process env is `--env` / `--inherit-process`. `elif`/`while`/`for` are parse errors, not `no status for: elif true`.

7. **One identity for `false`.** Either model `false` / `/usr/bin/false` / `/bin/false` as the same builtin (and refuse assignment prefixes / `!` / `command` / `env` with a one-line "not a prefix"), or require `--status` for all of them. Do not split the harvest analogue from the binary the log actually ran.

8. **Ingest the observation or stop implying it.** Either parse `bash: >` (and only that) so `demo.sh` is not a handwritten fold that already contains `--status 1`, or keep snippet+statuses and drop YAML from the dogfood story. Still do not run Bazel. Still do not treat `;` last-status as this lie.

If the mutation cannot do (1)+(2)+(3), the object is still `bash -x` plus a recorded 1 with extra print, and a later destroyer should KILL.

---

MUTATE
