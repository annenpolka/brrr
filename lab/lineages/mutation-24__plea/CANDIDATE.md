# mutation-24 — plea

## Primitive

A review stream is a set of before→after image claims; `plea` reports how **HEAD** occupies each claim (APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED), not whether GitHub marked the comment outdated.

## Flipped assumption

Ancestor **sate** occupies a *git range / unified diff*. `--suggest` is a sidecar that turns a ` ```suggestion ` fence into a one-hunk patch by taking **every `+` line of `diff_hunk`** as the before-image. That is the wrong object: a GitHub comment's before-image is the *commented range* (`start_line`…`line` / `original_*`), and the hunk is truncated at the comment. sate discarded `taken` as "sate with a different parser." The flip is the **input** (review stream, not a range) and the **reconstruction** (range, not all-plus), with default occupancy **against HEAD** (dirty worktree is `--worktree`).

## Why this might not exist

GitHub "outdated" is line-identity. `git apply --check` never saw a review comment. `sate --suggest` on cli/cli #333030758 would claim a 3-line before-image (`currentBranch, err := …` / `if err != nil {` / `return &github.PullRequest{}, err`) because those are the `+` lines of a truncated 11-line hunk. The comment is on **line 347 only**. Occupancy of the wrong image is a lie.

The review sandwich: `plea --against $original_commit_id` is OPEN; after the author takes it, `--against HEAD` is TAKEN.

## How to run

```bash
./plea --help
./plea --selftest
./demo.sh
gh api repos/cli/cli/pulls/7/comments | ./plea -C /path/to/cli
./plea --sandwich fixtures/go-iotest.json -C fixtures/trees/iotest-head
./plea fixtures/stream.md --worktree -C .
```

Exit: `0` unanimous APPLIED, `1` unanimous PENDING, `2` SPLIT / MIXED / DUPLEX / SUPERSEDED, `3` error.

## Empirical transcript

### v1 (range reconstruction + stream collide; whole-file occupancy)

`./plea --selftest` → 16 passed.

`./demo.sh` → **22 passed, 0 failed** (cli DUPLEX recorded, not asserted OPEN).

Reconstruction on the real cli/cli hunk (PR #7, comment 333030758):

- sate-all-plus before = 3 lines
- plea range before = `		return &github.PullRequest{}, err` only
- after = `		return nil, err`

Sandwich on a temp repo: default `--against HEAD` stays APPLIED when the worktree is reverted; `--worktree` is PENDING; `--sandwich` reports `then=PENDING` at `original_commit_id`.

Real GitHub comments vs file snapshots:

| comment | orig tree | HEAD-like snapshot |
| --- | --- | --- |
| golang iotest #466704840 (add `.` to doc comment) | OPEN | **TAKEN** |
| golang unixsock #611245425 (`// go:build` → `//go:build (js && wasm) \|\| windows`) | OPEN | **STALE** (HEAD is `//go:build js \|\| wasip1 \|\| windows`) |
| golang zip #720912639 (drop blank line, `start_line`–`line`) | OPEN | **STALE** (`readDataDescriptor` rewritten) |
| empty suggestion #225924481 (delete stray `w`) | OPEN if `w` remains | TAKEN if gone |

cli/cli #333030758 vs the *original* `command/pr.go` (597 lines at `625ff56`):

```
DUPLEX  command/pr.go  #333030758  exact-both  before@[346] after@[353]
DUPLEX  command/pr.go  #333031216  exact-both  before@[399] after@[457, 462]
SUPERSEDED  command/pr.go  #335420325  neither
```

The first suggestion is still open — line 347 is `return &github.PullRequest{}, err` — but line 354 of the **same function** is already `return nil, err`. Whole-file occupancy DUPLEXes a generic after-image that lives seven lines later. #333031216 is the same lie. That is the v1 failure.

### v2 (locus-anchored DUPLEX)

When both images hit, keep only hits that overlap `start_line`…`line` (±2). A generic after-image elsewhere in the function is `after-elsewhere`, not a copy of *this* plea.

```
PENDING  command/pr.go  #333030758  exact-before-locus  after-elsewhere@[353]
PENDING  command/pr.go  #333031216  exact-before-locus  after-elsewhere@[457, 462]
```

True DUPLEX fixtures (two function bodies, no line numbers) still DUPLEX: unknown locus ⇒ every hit counts.

`./plea --selftest` → **17 passed**. `./demo.sh` → **22 passed, 0 failed**, now asserting OPEN on the two cli comments.

## Dogfood targets

- `fixtures/cli-pr7.json` + `fixtures/trees/cli-orig/command/pr.go` (real GitHub API shape, `\r\n`, truncated hunks)
- `fixtures/go-*.json` + orig/head snapshots of iotest / unixsock / zip from golang/go
- markdown `fixtures/stream.md`, collide JSONL, temp-git sandwich

## Surprises

- GitHub `line` is null on almost every "outdated" comment; `original_line` is the real pointer. Occupancy must ignore GitHub's outdated bit.
- `diff_hunk` is truncated at the comment line. Range reconstruction still works because the last new-side line *is* `original_line` when you count from the `@@` header.
- An empty ` ```suggestion ` fence is a delete. `split('\n')` on empty would invent a blank line; `splitlines()` does not.
- Default-against-HEAD is the opposite of sate's worktree default. A dirty revert is invisible until `--worktree`.
- The reviewer's after-image on cli/cli PR #7 already existed seven lines later in the same function. Whole-file occupancy cannot tell "they already write `return nil, err` over there" from "they took this suggestion." The locus is the object GitHub actually pointed at.

## Failures

- Path-only: cli/cli moved `command/pr.go` → `pkg/cmd/pr/pr.go`. HEAD at the original path is missing-file SUPERSEDED even if the after-image lives under the new path.
- Locus slack is ±2 lines. A suggestion applied with a 10-line insert above the comment will miss the locus and fall through to off-locus DUPLEX / SUPERSEDED.
- unixsock HEAD is STALE even though the *spirit* landed (`//go:build` space removed; syntax rewritten again). Occupancy is of images, not intent.
- Quote-only comments (no ` ```suggestion `) are skipped.
- Threads are collide/echo via `in_reply_to`, not a thread fate.

## Suggested mutations

- Search the tree for a missing path (MOVED / APPLIED-elsewhere). cli/cli is the fixture.
- `plea --pick OPEN` emit an apply-able patch of still-open suggestions.
- Occupancy of *intent* for build tags / equivalent rewrites (unixsock).
- `--quotes`: a comment without a fence is a still-true predicate on the reconstructed line.

## Kill / keep

**Keep.** The flipped assumption is the input (review stream, not a git range) and the reconstruction (commented range, not all-plus). Locus occupancy is what made that object tell the truth on a real GitHub thread sate would DUPLEX. The sandwich held. Do not grow a patch parser or `--git`/`--log` back; that is sate.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | plea` is the interaction. No `git show`.
- Range reconstruction vs sate-all-plus is a measured bugfix on cli/cli PR #7.
- Default HEAD hides dirty reverts; `--worktree` opts in. Review occupancy is about the branch, not the editor.
- Collide/echo is a stream verb sate cannot have (one patch at a time).
- Empty suggestion = delete; multiline `start_line`; LEFT-side deleted lines.

**Lost**

- Occupying a stash or `main...HEAD` is out of scope. Pipe that to sate.
- GitHub outdated is still unused (deliberate: it is line-identity).
- No walker when the path is gone. MOVED is the next mutation.
