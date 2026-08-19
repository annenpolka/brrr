# hybrid-08 — lodge

## Primitive

A hunk and a review suggestion are the same before→after image claim; `lodge` occupies mixed input (git range + suggestion stream) with one kernel and one status vocabulary, fusing equal cores — including across a range rewrite — into `via=both`.

## Why this might not exist

sate occupies a *git range / unified diff*. plea occupies a *review stream*, with TAKEN/OPEN/STALE aliases and range reconstruction. Developers who have both still have two reports: `sate --git main...HEAD` and `plea comments.json`. Concatenation cannot say "this suggestion *is* that hunk," and it cannot say it when the range *renamed the file*.

The reviewer question is one occupancy: *does this tree occupy this change, and who claimed it — the range, the stream, or both?* GitHub outdated is line-identity. `git apply --check` is a boolean. `sate --suggest` takes every `+` line of a truncated hunk as the before-image.

Discarded as concatenation: wrapping sate and plea, printing two sections, or keeping plea's aliases next to sate's fates. The object changed: mixed claims enter one kernel; equal cores collapse; the range is a path map.

## How to run

From the worktree root:

```bash
chmod +x ./lodge
./lodge --help
./lodge --selftest
./demo.sh
./lodge --git HEAD comments.jsonl -C /path/to/repo
./lodge --git main...HEAD -C /path/to/repo
./lodge --worktree -C fixtures/trees/cli-orig fixtures/cli-pr7.json
```

Python 3.10+, stdlib, git. Exit 0 unanimous APPLIED, 1 unanimous PENDING, 2 SPLIT/MIXED/DUPLEX/SUPERSEDED, 3 error. `--report-only` forces 0. Default `--against HEAD` in a git repo; `--worktree` opts in.

## Empirical transcript

### v1 (`582ac3d`) — exact-core fuse, demo 34/0

`./lodge --selftest` → 14 passed. `./demo.sh` → **34 passed, 0 failed**.

Money shot on a temp repo (t0 `x=1`, t1 `x=2`, review stream the same bump):

```
./lodge --git HEAD comments.jsonl   →  n=1  APPLIED  via=both
./lodge --git HEAD --against HEAD^  →  PENDING  (fused sandwich)
./lodge --no-fuse --git HEAD …      →  n=2  (the concatenation the joint refuses)
```

Different after-images at the same locus stay two occupancies (hunk APPLIED, plea SUPERSEDED) and collide. One vocabulary: JSON has `fate` + `via`, no `alias`. cli/cli #333030758 reconstructs the commented range (not all-plus) and is PENDING at locus, not DUPLEX. iotest/unixsock/zip orig/head snapshots match plea. Prefix rule: voidtrace/tenaoshi `--git HEAD --against HEAD` unanimous APPLIED (sate v1's addition-DUPLEX).

kizu mixed with a suggestion equal to HEAD's `Cargo.lock` version bump: **via=both APPLIED** plus the leftover `Cargo.toml` hunk. Exact-core fusion paid rent on a real commit.

v1 failures, forced by mixed dogfood:

1. **golang iotest #466704840 + the file's orig→head patch.** The comment asks for a period on `// ErrTimeout is a fake timeout error`. Hunk #2 of the range also rewrites the next doc comment. v1: `covers` *and* `collide`, plea `via=plea`. The range contained the suggestion; collide is a lie.
2. **cli/cli shape: comment on `command/pr.go`, range deletes it and creates `pkg/cmd/pr/pr.go` already holding the after-image.** v1: plea SUPERSEDED missing-file, two hunks APPLIED. Concatenation says the same. Only mixed input knows the rewrite.

### v2 — range as a path map; subset is via=both echo

Forced by those two mixed runs, not a feature list:

1. **Subset cover.** A plea whose plus is a contiguous subset of a hunk's plus at overlapping locus is `via=both` without collapsing the hunk. annotate treats `covers` as echo, not collide.
2. **Range aliases.** Rename headers, and a 1:1 delete+create (or a create whose plus equals a plea on a deleted path), rewrite the comment onto the live path. Occupancy is at the new path; `moved_from` names the comment's path.

iotest mixed vs HEAD snapshot after v2:

```
via hunk=3 both=1  unanimous=APPLIED
466704840  via=both  APPLIED  covers=hunk:reader.go#2
```

Rename fixture after v2:

```
via both=1 hunk=1  unanimous=APPLIED
mislav  pkg/cmd/pr/pr.go  via=both  APPLIED  from=command/pr.go
```

`--no-fuse` on the same tree is still the two-row SUPERSEDED lie.

`./lodge --selftest` → **15 passed**. `./demo.sh` → **36 passed, 0 failed**. Sandwiches still unanimous APPLIED/PENDING on kizu, sitbone, voidtrace, tenaoshi, relico.

## Dogfood targets

- Synthetic mixed git repo (fuse / collide / sandwich / dirty-worktree / delete+create rewrite)
- `fixtures/cli-pr7.json` + `fixtures/trees/cli-orig` (truncated GitHub hunk, locus)
- `fixtures/go-iotest.json` mixed with orig→head patch of `reader.go`
- `fixtures/go-*.json` orig/head snapshots
- kizu HEAD mixed with an echo of the `Cargo.lock` version bump
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,voidtrace,tenaoshi,relico}` `--git HEAD` sandwich

## Surprises

- Equal-core fusion on kizu HEAD is a lockfile version ratchet (`0.6.0`→`0.7.0`) plus a leftover `Cargo.toml` hunk. That is occupancy of a *change*, not of a file.
- iotest's "add a period" comment lives *inside* a hunk that also changed the next sentence. Collapse would throw away the rest of the hunk; via=both on the plea keeps both grains.
- git often records a taken suggestion + path move as delete+create, not `rename from`/`rename to`. The 1:1 delete+create alias is load-bearing; rename headers alone would miss cli/cli.
- Default-against-HEAD hides a dirty revert of a fused claim the same way plea hid a dirty revert of a suggestion. The sandwich still holds.
- voidtrace/tenaoshi addition hunks are APPLIED, not DUPLEX: the prefix rule has to live in the *same* kernel as locus, or mixed input reintroduces sate v1's lie on one origin and not the other.

## Failures

- Path rewrite is 1:1 delete+create, or cores_equal against a create while the plea path was deleted. Two deletes and two creates in one range are not paired by filename similarity.
- Locus slack is still ±2. A suggestion applied under a 10-line insert above the comment misses the locus and will not subset-fuse.
- unixsock HEAD is SUPERSEDED even though the spirit landed (`//go:build` space removed; syntax rewritten again). Occupancy is of images, not intent.
- Quote-only comments (no ` ```suggestion `) are skipped.
- `--log` is out of scope (sate's walker). Pipe `git show` / `git diff` in; lodge sniffs.
- Binary patches SKIP/BINARY.

## Suggested mutations

- Pair N deletes to N creates by plus/minus cores, not 1:1.
- `--pick PENDING --format patch` emit still-open suggestions as an apply-able patch.
- Occupancy of *intent* for build tags / equivalent rewrites (unixsock).
- `--quotes`: a comment without a fence is a still-true predicate on the reconstructed line.

## Kill / keep

**Keep.** The object changed. Demo case 2 is a mixed `--git HEAD` + JSONL on which sate would print an APPLIED hunk and plea an APPLIED suggestion — two rows — and lodge prints **one** `via=both`. Demo case 12 is a tree on which plea is SUPERSEDED missing-file and sate is two APPLIED hunks, and lodge is `via=both` at the new path. v2 came from iotest's period living inside a larger hunk and from git recording a taken+moved suggestion as delete+create, not from concatenating `--suggest` onto `--git`.

Kill only if a later generation proves that `sate --git; plea` plus a hand-written path map recovers via=both — it does not, because discovering that the range *is* the suggestion (equal cores, or plus-subset, or rewrite) is the object.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | lodge --git main...HEAD` is the interaction. One kernel, one vocabulary.
- via=both is a fact neither parent can emit.
- Range reconstruction vs sate-all-plus still holds (cli/cli #333030758).
- Prefix rule and locus live together, so mixed input does not reintroduce either parent's lie.
- Delete+create rewrite is a mixed-only join: the range is the path map.

**Lost**

- `--log` of historical patches (sate). Pipe the patch in.
- TAKEN/OPEN/STALE aliases (plea). APPLIED/PENDING/SUPERSEDED are the names.
- A walker when the path is gone *and* the range did not record the move. MOVED-without-range is a later mutation.
