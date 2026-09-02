# swallowecho

Name the command whose nonzero exit was swallowed when a compound
command still exited 0.

`false || echo ok` prints `ok` and the step is 0. `bash -x` plus `$?`
shows the echo and the 0. It does not name **false** as the status that
disappeared. This query is that join.

`hidestatus` is the same CLI.

## Usage

```
swallowecho 'false || echo ok'
swallowecho --file snippet.sh
swallowecho -- false '||' echo ok
swallowecho --status 1 'bazel test //... || echo please regenerate'
```

| input | meaning |
| --- | --- |
| snippet | small shell list: simple commands, quotes, `\|\|`, `&&`, `\|`, `;` |
| `--file PATH` | snippet from a file (`-` = stdin) |
| `-- WORD ...` | argv list; `\|\|` / `&&` are tokens, not one string |
| `--status N` | recorded status for the next unexecuted pipeline (repeatable) |
| `--env NAME=VALUE` / `--unset NAME` | environment for `[[ -z $NAME ]]` |
| `--no-process-env` | start that environment empty |

Safe heads (`true`, `false`, `echo`, `printf`, `:`, `set`, `[[`) are
modeled. Anything else (bazel, xargs, make) is not executed. Pass
`--status`. `[[ ... || ... ]]` is a test, not a command swallow.
`if` / `then` / `else` / `fi` are list statements.

## Output

```
step_status	0
swallow	yes
swallowed	false
swallowed_status	1
hid_by	echo ok
hid_status	0
operator	||
ran	false	1
ran	echo ok	0
```

| row | meaning |
| --- | --- |
| `step_status` | compound / workflow-step status (last executed command) |
| `swallow` | `yes` when a `\|\|` success hid a nonzero **and** the step is 0 |
| `swallowed` | command text whose nonzero did not become the step status |
| `hid_by` | succeeding right-hand side of `\|\|` |
| `ran` / `recorded` / `skip` | each pipeline, with status or skip reason |

`true && echo ok` is not a swallow: nothing failed.

```
step_status	0
swallow	no
ran	true	0
ran	echo ok	0
```

## Examples

```
swallowecho 'false || echo ok'
# swallowed	false
# step_status	0

swallowecho 'true && echo ok'
# swallow	no
```

Protobuf staleness workflow (specimen-043): scheduled branch is
`bazel query ... | xargs bazel test ... || echo Please run ./regenerate_stale_files.sh`.
The packet does not run Bazel. Record the test pipeline as 1 (echo in a
green log means the left-hand side ran and failed):

```
swallowecho --status 1 -- 'bazel query ... | xargs bazel test $BAZEL_FLAGS' '||' echo 'Please run ./regenerate_stale_files.sh to regenerate stale files'
# swallowed	bazel query ... | xargs bazel test $BAZEL_FLAGS
# hid_by	echo Please run ./regenerate_stale_files.sh to regenerate stale files
# step_status	0
```

## Boundary

Does not run Bazel or GitHub Actions. `$VAR` expands only inside `[[`.
`;` last-status (`false; echo ok`) is not this `\|\|` lie. A pipe
without `pipefail` is not this lie. `swallow` is `no` when the step is
still nonzero (`false || false`). `if` is only recognized at list
position, not after `&&`.
