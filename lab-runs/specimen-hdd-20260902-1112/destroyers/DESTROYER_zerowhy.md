# DESTROYER zerowhy

Date: 2026-09-02 13:16 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/hybrid-zerowhy/zerowhy`

sha256 `4c14757463394e9ab79a58256b86059cf07f87ff0de9c7f2380503639414ba6d`. Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-zerowhy-zerowhy/zerowhy/zerowhy` is byte-identical.

Origin claim: hybrid of `swallowecho` and `waitoneshot`. Classify a lying zero / green as **exactly one** of `swallowed-nonzero` | `abort-before-visit` | `observed-ok` | `unknown`. Concatenating parent stdout still leaves a hand join; the object is the XOR. Kind: USEFUL_COMPOSITION.

Happy path is real. Unit tests (36/36) pass. Demo rows:

```text
false || echo ok
  → why  swallowed-nonzero

--timeout 0 --wait-for-creation true
  → why  abort-before-visit

--timeout 0 --wait-for-creation false --object-exists true
  → why  observed-ok

both in one argv
  → why  unknown
    claims  swallowed-nonzero abort-before-visit
```

That is not enough. `classify()` is `uniq(parent claims); why = claims[0] if len==1 else unknown`. `decide_wait` is `waitoneshot.decide` with booleans. `decide_shell` is a thinner `swallowecho` (five always-modeled heads, no `if`, no `[[`, no `--status`). The pairing of snippet and wait flags is caller-invented. Constitution 13.5: a valid hybrid must expose a relation unavailable from concatenating parent outputs. The exclusive class reconstructs from those outputs. Kill is not yet: the *question* (exactly one why for **this** green) is real. The embodiment is a mashup calculator.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/hybrid-zerowhy/zerowhy
SW=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-swallowecho/swallowecho
WO=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-waitoneshot/waitoneshot.py
```

No merge onto `main`. This object is not a PATH install.

---

## What still works

The three owned analogues, and any other modeled `||` whose left head is `false` and whose script status is 0, and any other timeout-0 creation-wait abort / oneshot visit of an existing object, **when only one parent channel is supplied**.

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

Honesty, same bytes, bash / parent:

```bash
bash -c 'false || echo ok'; echo bash:$?
# ok / bash:0
python3 "$SW" 'false || echo ok'   # swallow	yes  step_status	0
python3 "$WO" --timeout 0 --wait-for-creation true --object-exists true
# visited  false  abort  wait-for-creation-requires-timeout
```

Neighbors the tests already own:

| input | why |
| --- | --- |
| `true && echo ok` | `observed-ok` |
| `false; echo ok` | `unknown` (`;` last-status is not this `\|\|`) |
| `false \| echo ok` | `unknown` (pipe last-status is not this `\|\|`) |
| `false \|\| false` | `unknown` (step 1) |
| `true && false \|\| echo y` | `swallowed-nonzero` |
| timeout 0, `--for delete` | `observed-ok` (creation-wait ignored) |
| timeout 0, wait-for-creation false, missing object | `unknown` (no visit, no abort) |
| `make test \|\| true` | rc=2 `unmodeled` |
| empty argv | rc=2 `need a snippet, -- WORD ..., or --timeout` |
| `--wait-for-creation true` without `--timeout` | rc=2 |

`set -o pipefail` is unmodeled (rc=2), not `ran 0` plus skipped hid. That is stricter than `swallowecho`. Unmodeled heads and unsupported syntax refuse cleanly. Huge `true &&` × 2000 and a 1 MB echo arg return rc=0 in ~0.1s with a 89-byte report. Stdin without args is rc=2, not a silent read of the pipe.

That is the whole useful delta. Attacks below break the claim that `why` is an exclusive class of **one** green, or show the fold is parent-stdout uniq.

---

## Implementation

### 1. The exclusive class is reconstructable from concatenating the parents

Host-executed fold: `swallow yes` → `swallowed-nonzero`; `abort wait-for-creation-requires-timeout` → `abort-before-visit`; `visited true` → `observed-ok`; `swallow no` and every `ran` status 0 → `observed-ok`; two distinct names → `unknown`. Same `why` as this CLI on the demo rows **and** on the join holes in §2–3.

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

`decide_wait` is the parent table (`timeout == 0` and `wait_for_creation` and `for_cond != "delete"` → abort; missing + creation-wait + `timeout > 0` → not visited; else `visited = exists or for_cond == "delete"`). Negative, NaN, and inf timeouts take the same last branch as waitoneshot: **visited**.

### 2. Unnamed lying zeros do not enter the XOR — a named parent wins

README: `false; echo ok` is `unknown` because `;` last-status is not this swallow. `claims_from` only emits `swallowed-nonzero` / `observed-ok` / `abort-before-visit`. Step 0 without `||` swallow and without `all_ok` is **no claim**. Wait miss (`visited false`, `abort none`) is **no claim**.

So a semicolon green plus an abort is not `unknown`. It is abort:

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

`false; echo ok` is a lying zero bash will print as status 0. The exclusive class hides it behind the wait abort because semicolon is not a parent-named claim. The advertised join ("two reasons → unknown") only fires for **named** parent reasons. `true && echo ok` plus abort **does** refuse (`claims  observed-ok abort-before-visit`), because `all_ok` is a claim. Same step 0, two different XOR outcomes, depending on whether the shell channel happened to use `&&` or `;`.

Wait miss plus a shell success is the other hide:

```bash
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists false 'true && echo ok'
```

```text
why  observed-ok
claims  observed-ok
detail  compound succeeded
```

The wait did not visit and did not abort. Exclusive class is still `observed-ok`. Half the evidence is a miss and does not vote.

### 3. A red shell plus a wait green is `observed-ok`

The object is supposed to classify a lying **zero**. `false || false` is step 1. Combine it with a oneshot visit of an existing object:

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

There is no shell zero. Wait visited, so wait claims `observed-ok`, shell claims nothing (`step_status != 0` and not swallow), uniq length 1. The exclusive class of "this green" is the wait's, while the snippet you also typed is red. The CLI still exits 0 and does not say the channels disagree about whether anything was green.

### 4. Modeled `printf` is `observed-ok`; bash hid

`SAFE_HEADS`: `true`/`echo`/`printf`/`:` → 0, `false` → 1. No argv is a failure.

```bash
python3 "$CLI" 'printf || echo hid'
# why  observed-ok
# claims  observed-ok
# detail  compound succeeded
# rc=0

bash -c 'printf || echo hid'; echo bash:$?
# printf: usage: printf [-v var] format [arguments]
# hid
# bash:0
```

bash ran the hid. The tool skipped it and classified the green as observed-ok. That is unsupported certainty: the interpreter did not run `printf`. It returned 0 by construction. `printf "%s"` happens to be 0 in both, so the always-0 model is accidentally right on the formatted spelling and wrong on the harvest-shaped empty `printf`.

`/usr/bin/false || echo ok` is unmodeled (rc=2). bash on this host swallows it (status 0, prints ok). Same analogue, two identities: modeled `false` is a class; the binary is a refuse. `FALSE`, `command false`, `env false`, `FOO=1 false`, `! false` are all unmodeled. `false extra` stays modeled status 1 (bash `false` ignores args — this one matches).

### 5. Timeout identity: `== 0` after float parse

`oneshot = timeout == 0`. argparse `type=float`.

| argv | float | why (default creation-wait true, exists true) |
| --- | --- | --- |
| `--timeout 0` / `0.0` / `-0.0` / `00` | `0.0` | `abort-before-visit` |
| `--timeout 1e-400` | underflows to `0.0` | `abort-before-visit` |
| `--timeout 1e-323` / `1e-20` / `0.0000001` | tiny positive | `observed-ok` (visit) |
| `--timeout -1` / `-0.1` | negative | `observed-ok` (visit) |
| `--timeout nan` / `inf` / `-inf` (`--timeout=-inf`) | NaN/±inf | `observed-ok` (visit) |
| `--timeout -inf` (space, not `=`) | argparse "expected one argument" | rc=2 |
| `--timeout foo` | invalid float | rc=2 |

`--timeout 1e-400` is the same class as timeout 0 because IEEE underflow. `--timeout nan` is a successful visit of the default existing object. Parent waitoneshot does the same; the hybrid **prints `why observed-ok`** for a NaN budget. That is a lying green the wait parent at least labeled `visited true` / `oneshot false` without calling it ok.

`--timeout 5 --wait-for-creation true --object-exists true` is also `observed-ok` (`detail  object visited`). Oneshot vs wait-path is only a detail string. Positive timeout on a missing object is `unknown` / `claims none` / `did not visit and did not abort` — same token as semicolon last-status.

### 6. `--for` without `--timeout` is silently dropped; duplicate flags flip the class

`load_wait` treats extra wait evidence as `--wait-for-creation` or `--object-exists` only. `--for` is not extra.

```bash
python3 "$CLI" --for delete 'false || echo ok'
# why  swallowed-nonzero
# rc=0
```

`--for delete` is the flag that **disables** creation-wait abort in the parent. Here it is ignored, and the snippet classifies as if no wait channel existed. `--for delete` alone (no snippet) is `need a snippet, -- WORD ..., or --timeout` (rc=2), not "wait flags need --timeout".

`--for DELETE` / `--for foo` / `--for ''` with `--timeout 0` are abort (only exact `delete` is the exception). `--for delete --object-exists false` is `observed-ok` / oneshot visit: delete pretends the object was looked at even when the caller said it does not exist. Parent table; hybrid calls that `observed-ok`.

argparse last-wins, no error:

```bash
python3 "$CLI" --timeout 0 --wait-for-creation true --wait-for-creation false --object-exists true
# why  observed-ok   (abort flipped to visit)

python3 "$CLI" --timeout 0 --for delete --for jsonpath
# why  abort-before-visit   (visit flipped to abort)

python3 "$CLI" --timeout 0 --timeout 5 --wait-for-creation true --object-exists true
# why  observed-ok   (oneshot 0 flipped to wait-path visit)
```

Same flag name twice is two different exclusive classes. Tests never repeat a flag.

### 7. No `--status`; parent specimens cannot transfer

`swallowecho --status 1 'make test || true'` names the swallow. This CLI:

```bash
python3 "$CLI" --status 1 'make test || true'
# unrecognized arguments: --status
# rc=2

python3 "$CLI" 'make test || true'
# unmodeled command: make test
# rc=2

python3 "$CLI" 'kubectl wait --for=condition=Ready pod/x --timeout=0s || echo ok'
# unmodeled command: kubectl wait ...
# rc=2
```

specimen-043 workflow YAML as snippet is `unmodeled command: name: Staleness tests` (or the comment head). `if true; then false || echo hid; fi` is `unmodeled command: if true`. The hybrid is a **subset** of swallowecho plus a copy of waitoneshot. The CI step that created the swallow parent is not an input. The kubectl wait that created the wait parent is not an input. Flags are the wait observation; the caller already classified the abort.

Suggested mutation in CANDIDATE.md: "`--status N` for unexecuted pipelines". Absent. Unmodeled refuse is honest. It also means the exclusive class cannot be asked of either origin specimen.

### 8. Misleading exit zero; two-space fields; stdin unused

All four classes are CLI rc=0, including `unknown` and `step status is not 0`. CANDIDATE.md listed "Exit 1 on `unknown`". Absent. Fine as a printer; hostile as a pipe predicate. `false && echo ok` is bash rc=1 and this CLI rc=0 `why unknown`.

`claims  swallowed-nonzero abort-before-visit` is one field with an internal space. `awk -F '  '` gets the whole remainder; `cut -d' ' -f2` does not. Two classes are not two rows.

```bash
echo 'false || echo ok' | python3 "$CLI"     # rc=2 need a snippet
echo 'false || echo ok' | python3 "$CLI" -   # rc=2 unmodeled command: -
python3 "$CLI" --file -                      # argparse unrecognized --file
```

BOM before `false` is `unmodeled command: ﻿false` (rc=2). `# false || echo ok` is empty command (rc=2). `false || echo ok#hid` is `empty word near '#hid'`. `false || echo ok # comment` works. `$HOME` / `` `uname` `` are literal words (echo still 0, swallow still yes). `$(true)` is `unsupported (` (rc=2). NUL in argv is the OS (`ValueError: embedded null byte`), not a `zerowhy:` line.

---

## Primitive

Reality-stripped operation: optionally tokenize a tiny shell (`||` `&&` `|` `;`, five heads), optionally evaluate the waitoneshot flag table, collect at most two claim names, print the only name or `unknown`.

Nearest ordinary workflow: run `swallowecho` and/or `waitoneshot` (or `bash -x` plus `$?`, or read the wait error `wait-for-creation-requires-timeout`). Observable capability lost if zerowhy vanishes: the **named exclusive class** as one `why` line. That class is real when exactly one parent-named reason applies to **one** green. Concatenating the parents does not print `why`. A 15-line uniq over their fields does.

That is why this is not KILL: the *question* (which one reason is this green, or refuse) is a debugging object neither parent emits. The current embodiment is a mashup of independently supplied parent calculators that treats unnamed zeros as non-votes and will classify a red snippet plus a wait visit as `observed-ok`.

The ceiling is already written down, and it is too small for the claim:

- `why` = uniq of parent claim names, not a class of one observed event
- snippet and wait flags are not required to be co-located; pairing is argv order
- `;` / pipe last-status / step-nonzero / wait-miss do not vote, so a named abort or visit wins
- red shell + wait visit = `observed-ok`
- `printf` empty is `observed-ok` while bash hid
- `timeout == 0` after float parse: `1e-400` is abort, `nan`/`-1`/`inf` are visit
- `--for` without `--timeout` is dropped; duplicate flags last-win and flip the class
- no `--status`, no `if`, no YAML, no kubectl: origin specimens refuse
- all four classes rc=0; `unknown` is not a predicate
- `decide_wait` is the parent table, including delete-visits-a-missing-object

Do not grow a Bazel executor or a cluster waiter to escape this. Do not merge this fold into a general shell linter. Keep the exclusive-class row.

Constitution 13.5 (kill forced mashups) applies if the mutation cannot bind the two channels to one green. Dreamer ancestry is not protection. Concatenation-plus-uniq is not a hybrid.

---

## Mutation (what must change)

Keep the object: for **one** green, exactly one of `swallowed-nonzero` / `abort-before-visit` / `observed-ok` / `unknown`, and two named reasons must refuse.

Do not keep a uniq of two optional parent calculators.

1. **One green, not two stories.** Snippet and wait flags in one invocation must be evidence about the same step (a script that contains the wait, a log line, a recorded invocation). Independently typed `false || echo ok` plus kubectl-shaped flags is a mashup and must refuse (`unpaired-evidence`, rc≠0), not `unknown` and not a silent XOR. If the mutation cannot tell paired from unpaired, a later destroyer should KILL.

2. **Unnamed zeros vote.** `false; echo ok`, `false | echo ok`, step-nonzero, and wait-miss are claims (`semicolon-last-status` / `pipe-last-status` / `step-nonzero` / `no-visit`), not silence. `false; echo ok` plus abort is two reasons → `unknown`, not `abort-before-visit`. Red snippet plus wait visit is disagreement, not `observed-ok`. `true && echo ok` plus wait-miss is disagreement, not shell `observed-ok`.

3. **Do not `observed-ok` builtins you do not implement.** `printf` with no format: refuse or `--status`, not skip the hid and print `compound succeeded`. `timeout` not in `{0} ∪ (0, ∞)` (NaN, ±inf, negative, underflow-to-zero): rc≠0, never visit. `1e-400` must not be timeout 0.

4. **Wait flags are complete or absent.** `--for` without `--timeout` is an error, same as `--wait-for-creation`. Duplicate `--timeout` / `--wait-for-creation` / `--for` / `--object-exists` is an error, not last-wins class flip. `--for DELETE` vs `delete` is one identity or a refuse. `--for delete` plus `--object-exists false` must not be `observed-ok` without saying the visit was the delete exception.

5. **`--status` unused is an error; origin packets must classify or be a documented refuse.** Either accept recorded statuses so specimen-043 / `make test || true` can enter the XOR, or keep the unmodeled refuse and drop "CI step that has both a wait and a `|| echo`" from suggested mutations until that packet exists. `if`/`elif` are parse errors, not `unmodeled command: if true`.

6. **rc=1 on `unknown` and on step-nonzero.** rc=0 only for a single named class of an actual zero (`swallowed-nonzero` / `abort-before-visit` / `observed-ok`). CANDIDATE already wrote exit 1 on `unknown`. Cap huge argv. Two claim names are two rows or a repeated field, not `claims  a b`.

7. **Ingest the observation or stop implying it.** Either parse a wait error plus a `|| echo` in one snippet (and only that) so `demo.sh` is not two handwritten analogues glued by argv, or keep analogue flags and print `why` as `derived-from-flags`, not as a classified green. Still do not run Bazel. Still do not treat `;` last-status as this swallow.

If the mutation cannot do (1)+(2), the object is still parent concat plus uniq, and a later destroyer should KILL.

---

MUTATE
