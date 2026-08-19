# spar

Two review suggestions are a patch algebra, not a tree occupancy.

`twain` splits a *commit* into oracle-half vs production-half and occupies each half against a tree. `plea` occupies a suggestion against HEAD. **`spar` never reads a tree.** It composes the suggestions themselves:

| status | meaning | GitHub batch |
| --- | --- | --- |
| **COMMUTE** | either order, same after-image | safe |
| **ABSORB** | one after-image already contains the other | not (drop the inner) |
| **ORDERED** | only one order applies (chain) | not |
| **CONFLICT** | same locus disagrees, or neither order applies | not |

GitHub lets you "Add suggestion to batch" without saying whether two ` ```suggestion ` blocks commute, conflict, or one swallows the other. `git apply --check` is a boolean on one patch.

## Install / run

Python 3.10+, stdlib only. No git.

```bash
chmod +x ./spar
./spar --help
./spar --selftest
./demo.sh
gh api repos/cli/cli/pulls/7/comments | ./spar
./spar --all-commits comments.json   # pairwise across original_commit_id
./spar --patch oracle.patch prod.patch
./spar --emit a.jsonl b.jsonl
```

Default pairwise is **inside one `original_commit_id`**. A comments.json that mixed two PRs must not look GitHub-batch-safe.

Exit: `0` COMMUTE / EQUAL / EMPTY, `1` nested ABSORB / ORDERED, `2` CONFLICT, `3` error. `--report-only` forces `0`. `--json` / `--tsv` / `--porcelain` compose.

A GitHub comment's before-image is the *commented range* of `diff_hunk` (`start_line`…`line` / `original_*`), not every `+` line of a truncated hunk.

## Examples

**1. Two period-fixes on the same golang snapshot commute** (iotest PR #34741):

```bash
./spar fixtures/iotest-pair.json
# spar  COMMUTE  pairs=1  batch=yes
#   COMMUTE  src/testing/iotest/reader.go  466704840 × 466704931  either-order  @71×91
```

cli/cli PR#7's two `return nil` suggestions commute at @347×400. A third comment from PR#24 is a different snapshot and is skipped (v0.1 called that batch-safe).

**2. A large rewrite absorbs a one-line fix:**

```bash
./spar fixtures/absorb.jsonl
# ABSORB  app.py  big × tiny  nested  absorber=big
# exit 1 — apply `big`, skip `tiny`
```

**3. twain-style halves are two patches, not a mixed commit:**

```bash
./spar --patch fixtures/oracle.patch fixtures/prod.patch
# COMMUTE  disjoint-path  (tests × production)
./spar --patch fixtures/cut-prod.patch fixtures/cut-oracle.patch
# COMMUTE  same file, suffix cut, shared blank context
```
