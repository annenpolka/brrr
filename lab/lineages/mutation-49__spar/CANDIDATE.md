# mutation-49 — spar

## Primitive

Two review-suggestion patches are a patch algebra. `spar` composes them (COMMUTE / CONFLICT / ABSORB / ORDERED) without occupying a tree.

## Flipped assumption

Ancestor **twain** treats a *git commit* as two patches (oracle-half vs production-half) and occupies each half against a tree. Its suggested mutation was `spar`: compose `twain --emit` halves or review suggestions, not occupancy. The flip is the **object** (two ` ```suggestion ` patches, not a rev) and the **verb** (compose, do not occupy). plea/lodge still need HEAD. GitHub's batch button still has no algebra.

## Why this might not exist

Reviewers never compose two suggestion fences. GitHub "Add to batch" is untyped. `git apply --check` is a boolean on one mixed patch. twain's bind is token occupancy of a landed commit. None of them answer: *if I take both of these comments, does order matter, does one already contain the other, or do they fight?*

Discarded: occupy the suggestions (that is plea); grow twain with `--suggest` (that keeps the tree in the middle).

## How to run

```bash
chmod +x ./spar ./demo.sh
./spar --help
./spar --selftest
./demo.sh
./spar fixtures/iotest-pair.json
./spar --patch fixtures/oracle.patch fixtures/prod.patch
./spar --emit fixtures/absorb.jsonl
gh api repos/cli/cli/pulls/7/comments | ./spar
```

Python 3.10+, stdlib. No git. Exit 0 COMMUTE/EQUAL/EMPTY, 1 nested ABSORB/ORDERED, 2 CONFLICT, 3 error.

## Empirical transcript

### v0.1 (compose without a tree)

`./spar --selftest` → **24 passed**. `./demo.sh` → **23 passed, 0 failed**. Forced the grouping fix below; counts are historical.

Reconstruction on cli/cli #333030758 matches plea, not sate-all-plus: before is `return &github.PullRequest{}, err` (the commented line), not the three `+` lines of the truncated hunk.

| input | v0.1 |
| --- | --- |
| commute.jsonl (timeout × retries) | COMMUTE batch=yes |
| conflict.jsonl (TIMEOUT 60 vs 90) | CONFLICT exit 2 |
| absorb.jsonl (function rewrite × one-line fix) | ABSORB nested absorber=big exit 1 |
| ordered.jsonl (x=1→2 then 2→3) | ORDERED order=ab exit 1 |
| oracle.patch × prod.patch | COMMUTE disjoint-path |
| cut-prod × cut-oracle (shared blank) | COMMUTE either-order @1×4 |
| golang iotest #466704840 × #466704931 | COMMUTE either-order @71×91 |
| cli/cli PR#7+#24 harvest | **COMMUTE pairs=3 batch=yes** |
| go-suggestions.json (16 comments, mixed PRs) | **COMMUTE pairs=120 batch=yes** |

`--interesting` on go-suggestions hides 117 disjoint/unrelated and keeps three real same-snapshot pairs (iotest, code.html 218×221, go1.18.html 234×376). The headline still says batch=yes on 120 pairs.

### v0.2 (one improvement, two harvests)

Forced by that run, not a feature list: **pairwise stays inside `original_commit_id`**. `--all-commits` is the v0.1 cartesian. Cross-commit COMMUTE is not `batch=yes`.

After v0.2: `./spar --selftest` **30 passed**. `./demo.sh` **27 passed, 0 failed**.

```
$ ./spar fixtures/cli-pr7.json
spar  COMMUTE  pairs=1  batch=yes  commits=2  skipped=2  singles=1
  COMMUTE  command/pr.go  333030758 × 333031216  either-order  @347×400

$ ./spar --all-commits --interesting fixtures/cli-pr7.json
spar  COMMUTE  pairs=3  batch=no
  COMMUTE  command/pr.go  333030758 × 333031216  either-order  @347×400
  (2 disjoint/unrelated COMMUTE hidden)
```

PR#7's two `return nil, err` suggestions commute. PR#24 is a singleton on another snapshot; it no longer paints line 23 onto `625ff56`.

```
$ ./spar --interesting fixtures/go-suggestions.json
spar  COMMUTE  pairs=6  batch=yes  commits=11  skipped=114  singles=7
  COMMUTE  doc/code.html                 225924481 × 225924986  @221×218
  COMMUTE  src/testing/iotest/reader.go  466704840 × 466704931  @71×91
  COMMUTE  doc/go1.18.html               749073739 × 749073911  @234×376
  (3 disjoint-path unixsock COMMUTE hidden)
```

v0.1's 120-pair batch=yes is gone. `--all-commits` still prints 120.

## Dogfood targets

- `./spar --selftest` (30): v0.1 cases plus same-commit grouping, skipped=2, `--all-commits` restores 3, missing-commit jsonl still pairs.
- `./demo.sh` fixtures + emit + exit codes + grouped harvests.
- Real GitHub API shapes: `fixtures/cli-pr7.json`, `fixtures/iotest-pair.json`, `fixtures/go-suggestions.json`, `fixtures/go-zip.json`.

## Surprises

- A tests-first / prod-second split of a suffix-cut file **commutes** even when the hunks share a blank context line. Range overlap is not CONFLICT; sequential apply is.
- Empty ` ```suggestion ` is a delete (`after=[]`). `split('\n')` would invent a blank line; `splitlines()` does not. Same as plea.
- Bind (twain) of oracle×prod is about tokens. Compose of the same halves is disjoint-path COMMUTE. The halves can bind and still commute: occupancy is not algebra.

## Failures

- `--emit` of a COMMUTE pair is wholesale before→after hunks, not git's mixed context hunks. `git apply` still accepts them; they are uglier than `git show`.
- Partial overlap that is not nested is CONFLICT even when a line-level merge exists (`timeout = 60` vs `timeout = 30  # seconds`).
- `in_reply_to` is ignored; chain is image-only. GitHub replies keep the original `diff_hunk`, so a reply is usually a same-snapshot compose, not ORDERED.
- Combined merge diffs are not an input. There is no `-C`. Occupancy is plea.
- Comments with no `original_commit_id` share the empty key and still pairwise (jsonl fixtures). A mixed harvest that stripped commit ids would regress to v0.1.

## Suggested mutations

- Token-level commute on one line (comment + value).
- `--lock`: after COMMUTE, occupy the composed patch (plea on the emit). That is a hybrid, not spar.
- Brace-match / AST absorb (A rewrote the function and also renamed a helper B wanted).
- `--emit` as git-style mixed context hunks; compose three-way on a provided file *without* occupancy (the file is a before-image, not a tree).

## Kill / keep

**Keep.** The object changed: two suggestion patches, composed, no tree. MUTE/HOLLOW/LOCKED are occupancy of a commit. COMMUTE/ABSORB/ORDERED are what a reviewer needs *before* clicking Commit suggestion twice. v0.2's commit grouping is the difference between "this harvested JSON is batch-safe" and "these two comments on `625ff56` commute." Do not grow `-C` / HEAD occupancy back; that is plea.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | spar` is the interaction. No tree, no `git show`.
- COMMUTE on iotest @71×91 and cli/cli @347×400 is a reviewer verb GitHub's batch button does not have.
- twain `--emit` halves compose: oracle×prod is disjoint-path COMMUTE; a suffix cut with shared blank context still commutes.
- Nested ABSORB (drop the inner) is not occupancy and not `git apply --check`.
- v0.2 grouping made a mixed-PR harvest stop lying about batch safety.

**Lost**

- Occupying HEAD to see if a suggestion is TAKEN is out of scope. Pipe that to plea.
- No walker, no `-C`. The composed emit is an image, not a claim about a repository.
- Token bind (twain LOCKED) is gone: two halves can commute and still not mention each other.
