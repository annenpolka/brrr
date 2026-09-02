# DESTROYER waitoneshot 2

Date: 2026-09-02 15:34 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/waitoneshot`

sha256 `1041e255dd55524407633afa802ffde464a7b1dafe91d514b065ee3c940cce10` (`waitoneshot.py`, 2006 bytes, 56 lines). Launcher `waitoneshot` sha256 `1c3bd95e742455baaca1e5f045235deec92b53e4384f11c8f708c9e353005d01` (193 bytes, 5 lines `exec python3 waitoneshot.py`). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/waitoneshot-waitoneshot/waitoneshot/waitoneshot.py` is **byte-identical** (`cmp` rc=0). Worktree HEAD `3b2ddb30c70840e296e8744a03f4b72caf204cd7` (`Add waitoneshot CLI: timeout 0 visit vs wait-for-creation abort.`), branch `specimen-hdd/waitoneshot-waitoneshot`. Parent `main` is `432f954`; `git ls-tree` has no `waitoneshot`. Host Python 3.14.5. `kubectl` is on PATH (`/usr/local/bin/kubectl`) and **was not executed**. No cluster. No merge onto `main`.

Origin claim (`CANDIDATE.md` / harvest `hdd-k8s` / specimen-056 flag records, specimen-044 wait.go excerpt as origin only): one query names abort-before-visit versus a one-shot check when timeout 0 meets a creation-wait default. Kind: USEFUL_COMPOSITION. First destroyer (`DESTROYER_waitoneshot.md`) **KEEP**: the four harvest rows hold (timeout 0 + wait-for-creation true → abort, visited false; wait-for-creation false → oneshot visit; `for=delete` → oneshot; timeout 5 + missing → wait-path, visited false). First KEEP is not protection.

This candidate is a **THIN_WRAPPER of a flag table (timeout 0 + wait-for-creation) the caller already labeled**. `decide()` never reads `flags.txt`, never reads the wait.go excerpt, never starts a wait, never talks to a kube API. An independent replica of `decide()` plus argparse float formatting is **byte-identical** to CLI stdout on **392/392** argparse-accepted cells of a 420-cell grid (15 timeouts × 2 wait flags × 7 `--for` values × 2 exists). The 28 misses are all `--timeout -inf` (argparse treats `-inf` as a flag, rc=2). `--timeout=-inf` is accepted and matches the replica. awk of `t==0 && w==true && f!="delete"` matches `visited` / `oneshot` / `abort` on **10/10** harvest-shaped rows, including the first KEEP four. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/waitoneshot
PY=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/waitoneshot.py
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/fixtures
S056=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-056/files/flags.txt
S044=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-044/files/staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go.excerpt
```

No kubectl. Do not grow a wait / jsonpath / kube-API client to escape THIN_WRAPPER. Do not send kubectl theater back to R1. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Hybrid `emptyunit × waitoneshot` is already NON-JOIN. Sibling `zerowhy` already copies this table.

---

## What still works

The first KEEP four, and any other caller-typed `--timeout --wait-for-creation --for --object-exists` whose values already are the harvest row.

```bash
python3 "$CLI" --timeout 0 --wait-for-creation true --for jsonpath --object-exists true
echo rc=$?
```

```text
timeout  0.0
wait_for_creation  true
for  jsonpath
object_exists  true
visited  false
oneshot  false
abort  wait-for-creation-requires-timeout
reason  creation-wait default aborts before lookup when timeout is 0
rc=0
```

`--wait-for-creation false`: `visited true` / `oneshot true` / `abort none` / `reason one-shot check`, rc=0. `--for delete`: same oneshot visit, rc=0. `--timeout 5 --object-exists false`: `visited false` / `oneshot false` / `abort none` / `reason would wait for creation (not executed here)`, rc=0.

Unit tests 15/15 pass (`python3 tests/test_waitoneshot.py -v` → `Ran 15 tests in 0.214s` `OK`). `./demo.sh` twice: live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (1371 bytes, `cmp` rc=0). Direct `python3 waitoneshot.py` and the bash launcher emit the same abort stdout (sha256 `3abd1fda…`). Happy path is real. That is not enough. It is also what the harvest table already says.

---

## Implementation

`decide()` in full:

```python
def decide(timeout: float, wait_for_creation: bool, for_cond: str, exists: bool) -> dict:
    oneshot = timeout == 0
    if oneshot and wait_for_creation and for_cond != "delete":
        return {
            "visited": "false",
            "oneshot": "false",
            "abort": "wait-for-creation-requires-timeout",
            "reason": "creation-wait default aborts before lookup when timeout is 0",
        }
    if not exists and wait_for_creation and for_cond != "delete" and timeout > 0:
        return {
            "visited": "false",
            "oneshot": "false",
            "abort": "none",
            "reason": "would wait for creation (not executed here)",
        }
    return {
        "visited": "true" if exists or for_cond == "delete" else "false",
        "oneshot": "true" if oneshot else "false",
        "abort": "none",
        "reason": "one-shot check" if oneshot else "wait path",
    }
```

`decide.co_names` is `()`. `decide.co_varnames` is `('timeout', 'wait_for_creation', 'for_cond', 'exists', 'oneshot')`. There is no file, no duration parser, no `ToLower`, no Visit, no context deadline. `main` always returns 0 after argparse succeeds. `--wait-for-creation` / `--object-exists` are the strings `true`/`false`. `--for` is an unvalidated string, default `jsonpath`. `--timeout` is `argparse` `type=float`.

Owned `flags.txt` is a spectator. Tests assert the file contains `timeout=0` / `wait_for_creation=true`, then call `decide(0, True, "jsonpath", True)` with literals. `demo.sh` `cat`s the fixture and re-types the three CLI argv rows. The file is never parsed.

---

## Attacks (beyond first KEEP)

### 1. THIN_WRAPPER of the caller-labeled flag table

Harvest (specimen-056 `OBSERVED.md` / `flags.txt`):

```text
timeout=0 wait_for_creation=true for=jsonpath exists=true → abort, visited false
timeout=0 wait_for_creation=false for=jsonpath exists=true → oneshot visit
timeout=0 wait_for_creation=true for=delete exists=true → oneshot visit
```

Nearest ordinary workflow, no CLI:

```bash
# flags already labeled
t=0; w=true; f=jsonpath; e=true
if [ "$t" = 0 ] && [ "$w" = true ] && [ "$f" != delete ]; then
  echo "visited false abort wait-for-creation-requires-timeout"
fi
```

awk of the same three predicates matches CLI `visited`/`oneshot`/`abort` on the KEEP four plus missing-object abort, missing-without-creation-wait oneshot, delete-missing oneshot, positive-timeout existing, and `for=delete` missing-at-timeout-5 (**10/10**).

Independent Python replica (does not import `waitoneshot`) reprints CLI stdout byte-for-byte on every argparse-accepted grid cell. The product is the table. The canned `reason` lines are labels on those predicates.

Help text plus the error already name the join:

```text
timeout help: Zero means check once and don't wait
wait-for-creation default: true; ignored in --for=delete
error: --wait-for-creation requires a timeout value greater than 0
```

`waitoneshot --help` is argparse stubs. It does not mention `visited`, `oneshot`, `abort`, or abort-before-visit. The CLI relabels the error as `abort wait-for-creation-requires-timeout` and prints `visited false`. That is not a new question. The caller already chose which row.

### 2. `flags.txt` is not an input

```bash
python3 "$CLI" "$S056"; echo rc=$?
python3 "$CLI" --file "$S056"; echo rc=$?
printf '%s\n' "$(cat "$S056")" | python3 "$CLI"; echo rc=$?
printf '%s\n' "$(cat "$S056")" | python3 "$CLI" --timeout 0; echo rc=$?
```

Positional / `--file` / stdin-only: argparse rc=2, `the following arguments are required: --timeout`. Stdin with `--timeout 0`: default abort (`wait_for_creation true`), stdin ignored. The owned packet cannot enter except by the caller re-typing its fields as flags.

### 3. Existence is not consulted on the abort path

```bash
python3 "$CLI" --timeout 0 --wait-for-creation true --for jsonpath --object-exists true
python3 "$CLI" --timeout 0 --wait-for-creation true --for jsonpath --object-exists false
```

Both: `visited false` / `abort wait-for-creation-requires-timeout` / rc=0. `--object-exists` is echoed and unused. First KEEP already noted missing+positive-timeout is wait-path; this cut is that the abort row does not look at the object **whether or not the caller said it exists**. The “was the object visited?” question is answered from three flags, not from an object.

### 4. wait.go abort-before-`isForDelete`; harvest skips abort for `delete`

Owned excerpt (not executed):

```text
33: isForDelete := strings.ToLower(o.ForCondition) == "delete"
34: if o.WaitForCreation && o.Timeout == 0 {
35:     return fmt.Errorf("--wait-for-creation requires a timeout value greater than 0")
38: if o.WaitForCreation && !isForDelete {
```

kubectl would abort timeout-0 creation-wait **before** the delete exception. This CLI:

```text
--timeout 0 --wait-for-creation true --for delete
# visited true oneshot true abort none   (harvest / help-text “ignored in --for=delete”)
```

`--for Delete` / `DELETE` / ` delete` / `delete `: **abort**, because `for_cond != "delete"` is a case-sensitive string compare. kubectl `ToLower`. `--timeout 5 --for delete --object-exists false`: `visited true` / `reason wait path` (delete is treated as always-visited). `--timeout 5 --for Delete --object-exists false`: `would wait for creation`. The harvest table and the origin excerpt disagree on the load-bearing delete row. The CLI follows the table the caller already labeled, not the binary.

### 5. IEEE / argparse timeouts the first KEEP did not hit

| argv | timeout printed | visited | oneshot | abort | reason |
| --- | --- | --- | --- | --- | --- |
| `--timeout -0` / `-0.0` | `-0.0` | false | false | wait-for-creation-requires-timeout | abort (IEEE `-0.0 == 0`) |
| `--timeout 1e-400` / `1e-324` | `0.0` | false | false | wait-for-creation-requires-timeout | underflow is timeout 0 |
| `--timeout 1e-323` | `1e-323` | true | false | none | wait path (subnormal ≠ 0) |
| `--timeout nan` / `NaN` | `nan` | true | false | none | wait path, existing default |
| `--timeout nan --object-exists false` | `nan` | false | false | none | wait path (`nan > 0` is false) |
| `--timeout inf --object-exists false` | `inf` | false | false | none | would wait (not executed) |
| `--timeout=-inf --object-exists true` | `-inf` | true | false | none | wait path |
| `--timeout -inf` | (no stdout) | — | — | — | argparse rc=2 expected one arg |
| `--timeout -1` exists true | `-1.0` | true | false | none | wait path; kubectl “wait a week” is not this |
| `--timeout -1 --object-exists false` | `-1.0` | false | false | none | wait path, not would-wait (`-1 > 0` is false) |
| `--timeout 30s` / `0s` | — | — | — | — | rc=2; kubectl Duration refused |
| `--timeout 0.0000001` | `1e-07` | true | false | none | wait path |

`--timeout nan` with default exists is a successful visit of an object that was never looked at, labeled `wait path`. First KEEP called timeout 5 + missing “wait-path not oneshot.” NaN / negative / `-inf` take the last branch and still print `wait path` without waiting. `1e-323` vs `1e-324` is a lying split: one is wait-path visit, the other is the abort row, because IEEE underflow.

`--wait-for-creation True` / `yes` / `1` and `--object-exists True`: argparse rc=2. Closed enum of the harvest spelling.

### 6. Misleading exit zero; last-wins; huge `--for`

Abort and oneshot both rc=0. Documented (`CANDIDATE.md`: “Exit is 0 even on abort; the abort field is the object”). Fine as a printer; hostile as a predicate. `--timeout 0 --timeout 5`: last-wins, `timeout 5.0` / `abort none` / rc=0. `--for` of 100000 `x`: rc=0, abort (not `delete`), stdout 100204 bytes — the name is echoed, never evaluated as jsonpath.

### 7. `--for` is a sticker, not a condition

`--for jsonpath={.status.phase}=Running`, `--for condition`, `--for none`, `--for ''`: all abort at timeout 0 + default creation-wait. jsonpath is not evaluated. `delete` is the only token that changes the table, and only in that exact spelling.

---

## Primitive

Reality-stripped operation: take four caller-supplied flags; if `timeout == 0` and `wait_for_creation` and `for != "delete"`, print abort / visited false; elif missing + creation-wait + `timeout > 0`, print would-wait; else print `visited = exists or for=="delete"` and `oneshot = (timeout==0)`.

Nearest ordinary workflow: the awk / bash of those predicates, or reading help text plus `--wait-for-creation requires a timeout value greater than 0`. Observable capability lost if waitoneshot vanishes: **none**. The flags already are the input. The abort string is a hyphenation of the error. `visited` is not a visit.

That is why this is KILL, not MUTATE. The *question* (did timeout 0 still look at the object, or did a creation-wait default refuse before lookup?) is a real debugging object **when asked of a wait**. This embodiment asks it of flags the caller already classified. Adding `flags.txt --file`, rc=1 on abort, `ToLower(for)`, or a fourth row for abort-before-`isForDelete` would still be the table. Growing `kubectl wait` / a kube API / jsonpath Visit would be implementing the cluster theater the harvest rejected, and would be a new harvest, not a patch of this 21-line `if`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection.

Hardcoded ceiling:

- abort = `timeout==0 && wait_for_creation && for_cond!="delete"`
- existence unused on that path
- `delete` exact spelling; origin excerpt aborts first
- `oneshot` = `timeout==0` after the abort branch (IEEE `-0` / underflow count as 0)
- NaN / negative / `-inf` labeled `wait path` without waiting
- `flags.txt` never ingested
- always rc=0 on a classified row
- argparse stubs for help; no cluster

Honor KILL. Dreamer ancestry is not protection.

Do not grow a kubectl client or a jsonpath evaluator to escape THIN_WRAPPER. Do not merge onto `main`. No cluster. Do not send kubectl theater back to R1.

---

KILL
