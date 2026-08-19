# lodge

A hunk and a review suggestion are the same object: a before→after image claim. `lodge` occupies mixed input (git range + suggestion stream) with **one** kernel and **one** status vocabulary.

sate occupies a patch. plea occupies a stream (and speaks TAKEN/OPEN/STALE). Piping them is two reports. The joint is occupancy of a *change*: equal cores from opposite origins fuse into one row (`via=both`). Different cores at the same locus collide and stay two occupancies.

Not `git apply --check` (boolean). Not GitHub "outdated" (line-identity). Not `sate --suggest` (all `+` lines of a truncated hunk).

## Install / run

Python 3.10+, stdlib, `git`. No third-party packages. v0.2.

```bash
chmod +x ./lodge
./lodge --help
./lodge --selftest
./demo.sh
```

## Verdicts

| fate | meaning |
| --- | --- |
| APPLIED | after-image is in the tree; before-image is gone |
| PENDING | before-image is in the tree; after-image is absent |
| MIXED | both change-cores are tangled in the same region |
| DUPLEX | both images exist as independent blocks |
| SUPERSEDED | neither image; the world moved on |

| via | meaning |
| --- | --- |
| hunk | claimed only by the git range / patch |
| plea | claimed only by the review stream |
| both | equal cores fused: the range landed the suggestion |

Exit: `0` unanimous APPLIED, `1` unanimous PENDING, `2` SPLIT / MIXED / DUPLEX / SUPERSEDED, `3` error. `--report-only` forces `0`. Default `--against HEAD` in a git repo; `--worktree` opts in to the dirty tree.

## Examples

### 1. Mixed PR: did this range land this suggestion?

```bash
./lodge --git main...HEAD comments.jsonl -C /path/to/repo
gh api repos/cli/cli/pulls/7/comments | ./lodge --git HEAD -C /path/to/cli
```

Equal cores collapse to one occupancy `via=both`. Concatenation (`sate --git` plus `plea`) would print two APPLIED rows.

### 2. Range reconstruction, not all-plus

```bash
./lodge --worktree -C fixtures/trees/cli-orig fixtures/cli-pr7.json
```

cli/cli #333030758 comments on **line 347** (`return &github.PullRequest{}, err`). sate-all-plus would take three `+` lines. lodge reconstructs the commented range. A generic `return nil, err` seven lines later is not DUPLEX of *this* claim.

### 3. Occupancy sandwich, and a range that moved the file

```bash
./lodge --git HEAD --against HEAD
./lodge --git HEAD --against HEAD^
./lodge --git HEAD comments.jsonl   # comment on command/pr.go, range created pkg/cmd/pr/pr.go
```

A commit's own patch occupies HEAD as APPLIED and its parent as PENDING. Mixed with a matching review stream, the fused claim sandwiches the same way — one row, not two. If the range deleted the commented path and created another file already holding the after-image, lodge occupies **at the new path** (`moved_from` names the comment). plea on the same tree is SUPERSEDED missing-file.
