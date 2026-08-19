# plea

A review suggestion is not a boolean and not a git range. GitHub's "outdated" is line-identity. `sate --suggest` takes every `+` line of `diff_hunk` as the before-image. **`plea` occupies a stream of review claims against HEAD.**

| fate | alias | meaning |
| --- | --- | --- |
| **APPLIED** | TAKEN | after-image is in the tree; before-image is gone |
| **PENDING** | OPEN | before-image is in the tree; after-image is absent |
| **MIXED** | | both change-cores are tangled in the same region |
| **DUPLEX** | | both images exist as independent blocks |
| **SUPERSEDED** | STALE | neither image; the world moved on |

The object is a **review-occupancy vector**. Input is comments (`gh api …/comments`, JSONL, markdown ` ```suggestion ` fences), not `git show`. Default tree is **HEAD**, not the dirty worktree. Two pleas that share a locus and disagree **collide**; two that agree **echo**.

## Install / run

Python 3.10+, `git` only if `-C` is a repo (for `--against` / default HEAD). Stdlib only.

```bash
chmod +x ./plea
./plea --help
./plea --selftest
./demo.sh
```

## Examples

### 1. Did HEAD take the review?

```bash
gh api repos/cli/cli/pulls/7/comments | ./plea -C ~/src/cli
```

```
plea  stdin  n=3  unanimous=SPLIT  PENDING=2 SUPERSEDED=1
PENDING     command/pr.go  #333030758  exact-before-locus  recon=range
            after-elsewhere@[353]  OPEN
PENDING     command/pr.go  #333031216  exact-before-locus  recon=range  OPEN
SUPERSEDED  command/pr.go  #335420325  neither  recon=range  STALE
```

The occupancy sandwich: `plea --against $original_commit_id` is OPEN; after the author commits the suggestion, `--against HEAD` is TAKEN. `--sandwich` prints both.

### 2. A pasted review, no API

```bash
./plea fixtures/stream.md --worktree -C .
```

```
APPLIED     src/add.py      #md1:src/add.py  exact-after  TAKEN
PENDING     src/timeout.py  #md2:src/timeout.py  exact-before  OPEN
```

### 3. Two reviewers, one line

```bash
./plea fixtures/collide.jsonl --worktree -C .
```

```
PENDING     src/add.py  #alice  exact-before  collide:bob  echo:cara  OPEN
PENDING     src/add.py  #bob    exact-before  collide:alice,cara  OPEN
PENDING     src/add.py  #cara   exact-before  echo:alice  OPEN
```

Compose: `gh api …/comments | plea --tsv --pick OPEN | cut -f3,4`

## Flags

| flag | what |
| --- | --- |
| `-C DIR` | tree root |
| `--against REF` | read files from a git ref (default **HEAD** if git) |
| `--worktree` | occupy dirty files, not HEAD |
| `--sandwich` | also classify against each comment's `original_commit_id` |
| `--ignore-space` | collapse horizontal whitespace |
| `--fuzz` | accept a window with ≥0.85 line overlap |
| `--json` / `--tsv` / `--quiet` | machine output |
| `--pick` / `--only` | filter fates (`OPEN`/`TAKEN`/`STALE` aliases) |
| `--report-only` | always exit 0 |

Exit `0` unanimous APPLIED, `1` unanimous PENDING, `2` split / MIXED / DUPLEX / SUPERSEDED.

## Why this might not exist

`sate` occupies a patch. A GitHub review comment is not a patch: `diff_hunk` is truncated at the comment, `line` is often null ("outdated"), and the before-image is the *commented range* (`start_line`…`line`), not every added line of the hunk. `git apply --check` never saw this object. GitHub outdated never looked at the images.
