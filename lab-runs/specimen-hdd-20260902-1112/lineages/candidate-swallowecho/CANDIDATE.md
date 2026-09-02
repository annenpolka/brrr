# swallowecho

origin.method: specimen-hdd
origin.trial: hdd-pbci
specimens: [specimen-043]

classification: USEFUL_COMPOSITION

## Primitive

Report a compound command whose later success hid an earlier nonzero
exit (`|| echo` last-status lie). Name the swallowed command and the
resulting step status 0.

## Why this might not exist

The step log shows `echo` output and the job is green. `bash -x` plus
`$?` still presents status 0. The join — which command was nonzero, that
`||` ran a success, that the step inherited 0 — is a hand comparison.

## Core operation

Parse a small shell snippet or argv list. Model `||` / `&&` / `|` / `;`.
If a nonzero left-hand side caused a succeeding `||` right-hand side to
run and the compound status is 0, name that left-hand command.

## Observable delta

One query states `swallow yes`, `swallowed false`, `step_status 0`
instead of a green step. `true && echo ok` is `swallow no`.

## Reality mapping

Owned analogue: `false || echo ok` (executed). specimen-043 then-branch:
`bazel query ... | xargs bazel test $BAZEL_FLAGS || echo Please run
./regenerate_stale_files.sh` with `--status 1` for the unexecuted Bazel
pipeline. Echo in a successful Actions log is the observation that the
right-hand side ran.

## Research boundary

Does not run Bazel or GitHub Actions. Does not expand general `$VAR`.
Does not treat `;` last-status or pipe-last-status as this swallow.

## Removed

Host-executed Bazel stale-file logs. Workflow patch. Attaching `|| echo`
to `fi`.

## Smallest artifact

Python 3 stdlib CLI `swallowecho` (alias `hidestatus`).

## Pre-implementation Reality assessment

- Classification: USEFUL_COMPOSITION
- Nearest existing operation: `bash -x` plus reading `$?`
- Observable delta: names the swallowed status rather than the step's 0
- Constraint: snippet / argv list plus executed or recorded statuses
- Established on the analogue: `false || echo ok` → step 0 while false
  was 1; green job plus echo sentence on the protobuf workflow

## How to run

From this directory:

```
python3 tests/test_swallowecho.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` twice, identical.

Nearest existing:

```
ok
bash_step_status:0
```

`bash -c 'false || echo ok'` prints `ok` and status 0. It does not name
false.

```
== swallowecho 'false || echo ok' ==
step_status	0
swallow	yes
swallowed	false
swallowed_status	1
hid_by	echo ok
hid_status	0
operator	||
```

```
== swallowecho 'true && echo ok' ==
step_status	0
swallow	no
```

specimen-043 extracted then-body, `--status 1` (Bazel not run):

```
swallowed	bazel query 'attr(tags, "staleness_test", //...)' | xargs bazel test $BAZEL_FLAGS
hid_by	echo "Please run ./regenerate_stale_files.sh to regenerate stale files"
step_status	0
swallow	yes
```

Full folded workflow bash, scheduled (`COMMIT_TRIGGERED_RUN` /
`MAIN_RUN` unset), same swallowed pipeline. `[[ -z $COMMIT_TRIGGERED_RUN
|| -z $MAIN_RUN ]]` ran with status 0 and was not a swallow site.

Unseen `make test || true` with `--status 1`: swallowed `make test`,
`hid_by true`, step 0.

Tests: 24 OK (`python3 tests/test_swallowecho.py`).

## Dogfood targets

- `false || echo ok` / `true && echo ok`
- specimen-043 `.github/workflows/staleness_check.yml` bash step
- unseen `make test || true`

## Surprises

First run of the full workflow bash failed with `no status for: -z
$MAIN_RUN ]]`. The `||` inside `[[ -z $COMMIT_TRIGGERED_RUN || -z
$MAIN_RUN ]]` was treated as a command operator. Grouping `[[ ]]` and
parsing `if` / `then` / `else` / `fi` made one `--status 1` enough, and
the swallowed text is the bazel pipeline, not the test expression.

YAML `bash: >` folds newlines to spaces. The `|| echo` stays inside the
then-branch; it is not attached to `fi`.

## Failures

- Unexecuted commands without `--status` are a refusal, not a guessed
  failure.
- `false; echo ok` is step 0 without `swallow yes`.
- `false || false` is step 1, `swallow no`.
- `[[` supports `-z` / `-n` / `!` / `||` / `&&` only.
- `if` only at list position.

## Suggested mutations

- `--check` exit 1 on `swallow yes`
- Honor `set -o pipefail` as a separate pipe-hide
- Parse GitHub Actions YAML `bash: >` directly

## Kill / keep

Keep: `false || echo ok` names swallowed `false` with step 0.
`true && echo ok` is not a swallow. specimen-043 scheduled bash names
the bazel pipeline as swallowed, not the `[[ || ]]` test.
