# DESTROYER zerowhy 2

Date: 2026-09-02 15:46 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0390
Worker: destroyer-zerowhy-2

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/hybrid-zerowhy/zerowhy`

sha256 `4c14757463394e9ab79a58256b86059cf07f87ff0de9c7f2380503639414ba6d` (14981 bytes, 518 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-zerowhy-zerowhy/zerowhy/zerowhy` is **byte-identical** (`cmp` rc=0). Same digest as first destroyer. Worktree HEAD `f1e55728d7d8ee69b9a37c805b86e2e9edeb7ab6` (`Add zerowhy CLI: exclusive class for a lying zero.`), branch `specimen-hdd/hybrid-zerowhy-zerowhy`. Parent `main` is `432f954`; `git ls-tree main` has no `zerowhy`. Host Python 3.14.5. `kubectl` is on PATH (`/usr/local/bin/kubectl`) and **was not executed**. No cluster. No merge onto `main`. No `MUTATE.md` in the lineage. No `mutate-zerowhy` job exists.

Origin claim (`CANDIDATE.md` / hybrid of `swallowecho` × `waitoneshot`): classify a lying zero as exactly one of `swallowed-nonzero` | `abort-before-visit` | `observed-ok` | `unknown`. Kind: USEFUL_COMPOSITION. First destroyer (`DESTROYER_zerowhy.md`) **MUTATE**: the exclusive-class *question* was real; the embodiment was uniq of two independently supplied parent calculators. Mutation required (1) unpaired evidence refuse and (2) unnamed zeros vote, else a later destroyer should KILL. First MUTATE is not protection. Bytes unchanged.

Sibling `waitoneshot` was Honor-KILLed (`DESTROYER_waitoneshot_2.md`, `fossils/waitoneshot.md`) as a **THIN_WRAPPER of a flag table (timeout 0 + wait-for-creation) the caller already labeled**. `decide_wait` is that table. Wait-only `why` is a 3-line relabel of it. Independent replica of `decide()` plus that relabel matches CLI `why` on **420/420** cells of a 420-cell grid (15 timeouts × 2 wait flags × 7 `--for` values × 2 exists). awk of `t==0 && w==true && f!="delete"` matches `abort-before-visit` vs not on **420/420**, including **10/10** harvest-shaped rows. Host fold of parent stdout (no import of `zerowhy`) matches `why` on **15/15** mashup and single-channel rows. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/hybrid-zerowhy/zerowhy
WO=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/waitoneshot.py
SW=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-swallowecho/swallowecho
```

`waitoneshot.py` sha256 `1041e255dd55524407633afa802ffde464a7b1dafe91d514b065ee3c940cce10` (the Honor-KILLed table). No kubectl. Do not grow a wait / jsonpath / kube-API / Bazel executor to escape THIN_WRAPPER. Do not send kubectl theater back to R1. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Hybrid `emptyunit × waitoneshot` is already NON-JOIN (same mashup shape). Constitution 13.5: kill forced mashups.

---

## What still works

The three owned analogues, and the join that prints `unknown` when both parent-named claims are present. That is the first MUTATE leftover. It is also the table the caller already labeled.

```bash
python3 "$CLI" 'false || echo ok'
python3 "$CLI" --timeout 0 --wait-for-creation true
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists true
python3 "$CLI" --timeout 0 --wait-for-creation true 'false || echo ok'
```

```text
why  swallowed-nonzero
why  abort-before-visit
why  observed-ok
why  unknown
claims  swallowed-nonzero abort-before-visit
rc=0 all four
```

Unit tests 36/36 pass (`python3 tests/test_zerowhy.py` → `Ran 36 tests in 0.559s` `OK`). `./demo.sh` twice: live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (1114 bytes, `cmp` rc=0). Happy path is real. That is not enough. Wait-only rows are the harvest table with new nouns.

Honesty, same bytes, parent:

```bash
python3 "$WO" --timeout 0 --wait-for-creation true --object-exists true
# visited  false  abort  wait-for-creation-requires-timeout
python3 "$SW" 'false || echo ok'
# swallow	yes  step_status	0
```

---

## Implementation

`decide_wait` in full (parent `decide()`, booleans instead of `"true"`/`"false"` strings):

```python
def decide_wait(
    timeout: float,
    wait_for_creation: bool,
    for_cond: str,
    exists: bool,
) -> WaitEv:
    oneshot = timeout == 0
    if oneshot and wait_for_creation and for_cond != "delete":
        return WaitEv(
            visited=False,
            oneshot=False,
            abort="wait-for-creation-requires-timeout",
        )
    if not exists and wait_for_creation and for_cond != "delete" and timeout > 0:
        return WaitEv(visited=False, oneshot=False, abort="none")
    return WaitEv(
        visited=bool(exists or for_cond == "delete"),
        oneshot=oneshot,
        abort="none",
    )
```

`decide_wait.co_names` is `('WaitEv', 'bool')`. `decide_wait.co_varnames` is `('timeout', 'wait_for_creation', 'for_cond', 'exists', 'oneshot')`. There is no file, no duration parser, no `ToLower`, no Visit, no context deadline, no kube API.

Wait-only `why` is this relabel (no import of either CLI):

```python
if abort == "wait-for-creation-requires-timeout":
    why = "abort-before-visit"
elif visited:
    why = "observed-ok"
else:
    why = "unknown"
```

`claims_from` / `classify`:

```python
# shell: swallow → swallowed-nonzero; elif step 0 and all_ok → observed-ok
# wait:  abort  → abort-before-visit; elif visited → observed-ok
# unnamed zeros and wait-miss emit nothing
uniq = list(dict.fromkeys(raw))
why = uniq[0] if len(uniq) == 1 else "unknown"
```

`classify.co_names` is `('claims_from', 'list', 'dict', 'fromkeys', 'len', 'Verdict', 'tuple', 'detail_for')`. The exclusive class is `len(uniq)==1`. Concatenating the parents already contains both names.

`SAFE_HEADS` is `true`/`echo`/`printf`/`:` → 0, `false` → 1. `main` always returns 0 after a classified row.

---

## Attacks (beyond first MUTATE)

### 1. THIN_WRAPPER of the Honor-KILLed timeout-0 flag table

Harvest (specimen-056 / waitoneshot KEEP four, plus existence-unused abort):

```text
timeout=0 wait_for_creation=true  for=jsonpath exists=true  → abort-before-visit
timeout=0 wait_for_creation=false for=jsonpath exists=true  → observed-ok
timeout=0 wait_for_creation=true  for=delete   exists=true  → observed-ok
timeout=5 wait_for_creation=true  for=jsonpath exists=false → unknown (no visit, no abort)
timeout=0 wait_for_creation=true  for=jsonpath exists=false → abort-before-visit (exists unused)
```

Nearest ordinary workflow, no CLI:

```bash
# flags already labeled
t=0; w=true; f=jsonpath; e=true
if [ "$t" = 0 ] && [ "$w" = true ] && [ "$f" != delete ]; then
  echo "why  abort-before-visit"
fi
```

Independent replica of `decide()` (does not import `waitoneshot` or `zerowhy`) plus the three-line relabel reprints CLI `why` on **420/420** argparse-accepted cells. Same grid as the sibling Honor-KILL, with `--timeout=-inf` in equals form (space-separated `--timeout -inf` is argparse rc=2 on both CLIs, not a cell). awk of `t==0 && w==true && f!="delete"` matches `abort-before-visit` vs not on those **420/420**, and on **10/10** harvest-shaped rows.

The product is the table. `detail  timeout 0 aborted before visiting the object` is a label on those three predicates. `visited` is not a visit.

Sibling `waitoneshot --help` already names the join: “Zero means check once and don't wait”; error `--wait-for-creation requires a timeout value greater than 0`. This CLI relabels that error as `why abort-before-visit`. That is not a new question. The caller already chose which row.

### 2. Exclusive class reconstructs from concatenating the parents

Host-executed fold (no import): `swallow yes` → `swallowed-nonzero`; `abort wait-for-creation-requires-timeout` → `abort-before-visit`; `visited true` → `observed-ok`; `swallow no` and every `ran` status 0 → `observed-ok`; two distinct names → `unknown`; wait-miss / step-nonzero / semicolon last-status → no claim. Same `why` as this CLI on **15/15** rows: the three demos, the advertised join, semicolon+abort, pipe+abort, red snippet + oneshot visit, shell-ok + wait-miss, `printf || echo hid`, `--for delete` missing, timeout 5 missing, `false && echo ok`, `--timeout nan`, `--timeout 1e-400`.

```text
python3 "$SW" 'false || echo ok'
python3 "$WO" --timeout 0 --wait-for-creation true --object-exists true
# swallow	yes
# abort  wait-for-creation-requires-timeout
# (two reports; no exclusive why)

python3 "$CLI" --timeout 0 --wait-for-creation true 'false || echo ok'
# why  unknown
# claims  swallowed-nonzero abort-before-visit
```

The hybrid delta is `len(uniq(claims))==1`. Concatenation already contains both reasons. The CLI does not discover that the snippet and the wait flags describe the same event. You can XOR a bazel `|| echo` with a kubectl wait that never ran in that step.

### 3. First MUTATE (1)+(2) did not land

MUTATE required: unpaired snippet+flags must refuse (`unpaired-evidence`, rc≠0); unnamed zeros must vote. Absent. Bytes unchanged.

```bash
python3 "$CLI" --timeout 0 --wait-for-creation true 'false; echo ok'
python3 "$CLI" --timeout 0 --wait-for-creation true 'false | echo ok'
python3 "$CLI" --timeout 0 --wait-for-creation true 'false || false'
```

```text
why  abort-before-visit
claims  abort-before-visit
# all three, rc=0
```

`false; echo ok` is a lying zero bash prints as status 0. The exclusive class hides it behind the wait abort because semicolon is not a parent-named claim. Two independently typed stories still classify. First MUTATE said that is mashup and must refuse. It does not.

Wait-miss plus a shell success is the other hide:

```bash
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists false 'true && echo ok'
# why  observed-ok
# claims  observed-ok
```

The wait did not visit and did not abort. Exclusive class is still `observed-ok`. Half the evidence is a miss and does not vote.

### 4. A red shell plus a wait green is `observed-ok`

```bash
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists true 'false || false'
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists true 'false && echo ok'
```

```text
why  observed-ok
claims  observed-ok
detail  oneshot visit
rc=0
```

There is no shell zero. Wait visited, so wait claims `observed-ok`, shell claims nothing. The exclusive class of “this green” is the wait's, while the snippet you also typed is red. First MUTATE named this disagreement. Still `observed-ok`.

### 5. Modeled `printf` is `observed-ok`; bash hid

```bash
python3 "$CLI" 'printf || echo hid'
# why  observed-ok / detail  compound succeeded / rc=0

bash -c 'printf || echo hid'; echo bash:$?
# printf: usage: printf [-v var] format [arguments]
# hid
# bash:0
```

bash ran the hid. The tool skipped it and classified the green as observed-ok. `SAFE_HEADS['printf']=0` by construction. First MUTATE: do not `observed-ok` builtins you do not implement. Unchanged.

### 6. Timeout identity: `== 0` after float parse (parent table)

| argv | float | why (default creation-wait true, exists true) |
| --- | --- | --- |
| `--timeout 0` / `0.0` / `-0.0` / `00` | `0.0` | `abort-before-visit` |
| `--timeout 1e-400` | underflows to `0.0` | `abort-before-visit` |
| `--timeout 1e-323` / `1e-20` / `0.0000001` | tiny positive | `observed-ok` (visit) |
| `--timeout -1` / `-0.1` | negative | `observed-ok` (visit) |
| `--timeout nan` / `inf` / `--timeout=-inf` | NaN/±inf | `observed-ok` (visit) |
| `--timeout -inf` (space, not `=`) | argparse expected one argument | rc=2 |
| `--timeout 30s` / `0s` | kubectl Duration refused | rc=2 |

`--timeout 1e-400` is the same class as timeout 0 because IEEE underflow. `--timeout nan` is a successful visit of the default existing object, labeled `why observed-ok`. Parent waitoneshot at least printed `visited true` / `oneshot false` without calling it ok. The hybrid **prints ok**. First MUTATE: timeout not in `{0} ∪ (0, ∞)` must never visit. Unchanged.

`--timeout 5 --object-exists false`: `unknown` / `claims none` / `did not visit and did not abort`. `--for delete --object-exists false`: `observed-ok` (delete pretends the missing object was looked at). Parent table; hybrid calls that ok.

### 7. `--for` without `--timeout` is silently dropped; duplicate flags flip the class

```bash
python3 "$CLI" --for delete 'false || echo ok'
# why  swallowed-nonzero  rc=0
```

`--for delete` is the flag that **disables** creation-wait abort in the parent. Here it is ignored. First MUTATE: wait flags are complete or absent. Unchanged.

argparse last-wins, no error:

```text
--timeout 0 --wait-for-creation true --wait-for-creation false --object-exists true
  → why  observed-ok   (abort flipped to visit)
--timeout 0 --for delete --for jsonpath
  → why  abort-before-visit   (visit flipped to abort)
--timeout 0 --timeout 5 --wait-for-creation true --object-exists true
  → why  observed-ok   (oneshot 0 flipped to wait-path visit)
```

`--for DELETE` / `--for foo` / `--for ''` with `--timeout 0` are abort (only exact `delete` is the exception). `--for` of 100000 `x`: rc=0, abort, the name is echoed never evaluated as jsonpath.

### 8. Origin packets refuse; all four classes rc=0

```text
--status 1 'make test || true'     → argparse unrecognized, rc=2
'make test || true'                → unmodeled command: make test, rc=2
'kubectl wait ... || echo ok'      → unmodeled command: kubectl wait ..., rc=2
'if true; then false || echo hid; fi' → unmodeled command: if true, rc=2
```

The CI step that created the swallow parent is not an input. The kubectl wait that created the wait parent is not an input. Flags are the wait observation; the caller already classified the abort.

All four classes are CLI rc=0, including `unknown` and `step status is not 0`. CANDIDATE.md listed “Exit 1 on `unknown`”. Absent. First MUTATE: rc=1 on `unknown`. Unchanged. `false && echo ok` is bash rc=1 and this CLI rc=0 `why unknown`. Stdin without args is rc=2, not a silent read of the pipe.

---

## Primitive

Reality-stripped operation: optionally tokenize a tiny shell (`||` `&&` `|` `;`, five heads), optionally evaluate the waitoneshot timeout-0 flag table, collect at most two claim names, print the only name or `unknown`.

Nearest ordinary workflow: run `swallowecho` and/or `waitoneshot` (or `bash -x` plus `$?`, or read the wait error `wait-for-creation-requires-timeout`, or awk `t==0 && w==true && f!="delete"`). Observable capability lost if zerowhy vanishes: **none** on the wait channel (sibling already fossilized that table); on the join, a 15-line uniq over parent fields.

That is why this is KILL, not another MUTATE. The *question* (exactly one why for **this** green) is a debugging object **when asked of one observed event**. This embodiment asks it of flags the caller already classified, optionally XOR'd with a modeled `||`. First MUTATE already wrote the ceiling and said if (1)+(2) cannot bind the two channels to one green, a later destroyer should KILL. Mutation did not land. Sibling waitoneshot is Honor-KILL of the same table. Growing `kubectl wait` / a kube API / jsonpath Visit / a Bazel executor would be implementing the cluster theater the harvest rejected, and would be a new harvest, not a patch of this `if`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Do not send THIN_WRAPPER back to R1 with “make this more novel.” First MUTATE is not protection.

Hardcoded ceiling:

- wait `why` = relabel of `timeout==0 && wait_for_creation && for_cond!="delete"` / `visited` / else unknown
- `decide_wait` ≡ Honor-KILLed `waitoneshot.decide`
- existence unused on the abort path
- `delete` exact spelling; origin excerpt aborts first
- `oneshot` = `timeout==0` after float parse (IEEE `-0` / underflow count as 0)
- NaN / negative / `-inf` labeled `observed-ok` without visiting
- snippet and wait flags are not required to be co-located; pairing is argv order
- `;` / pipe last-status / step-nonzero / wait-miss do not vote, so a named abort or visit wins
- red shell + wait visit = `observed-ok`
- `printf` empty is `observed-ok` while bash hid
- `--for` without `--timeout` is dropped; duplicate flags last-win and flip the class
- no `--status`, no `if`, no YAML, no kubectl: origin specimens refuse
- all four classes rc=0; `unknown` is not a predicate
- `flags.txt` / wait.go never ingested

Honor KILL. Dreamer ancestry is not protection. Concatenation-plus-uniq is not a hybrid.

Do not grow a kubectl client or a jsonpath evaluator to escape THIN_WRAPPER. Do not merge onto `main`. No cluster. Do not send kubectl theater back to R1. Reimpl of this primitive is not a survivor.

---

KILL
