# hybrid-12 — braid

## Primitive

Compose review-suggestion strands first (refuse on JAM/SPLIT), then occupy the **single composed after-image** against a tree — one occupancy of the union/fold, not N strand rows.

## Why this might not exist

plait/spar answer "do these comments compose?" and stop. sate/plea/lodge occupy *each* claim. GitHub "Commit suggestion" is one click per fence; "Add to batch" is untyped. `git apply --check` is a boolean on one mixed patch.

The reviewer question after "they commute" is occupancy of *that* result: if I take both, is the union already in HEAD? If round 2 stacks on round 1, does HEAD occupy `beta→beta3`, or only the leftover `beta2`? Concatenating `plait | sate` prints two fates and cannot say SUPERSEDED of the composed image when only A has landed.

Discarded: piping the CLIs; occupying each strand and joining rows; growing plait's schedule table (`same-tree` of three apply orders).

## How to run

```bash
chmod +x ./braid ./demo.sh
./braid --help
./braid --selftest
./demo.sh
./braid -C fixtures/trees/commute fixtures/commute.jsonl
./braid fixtures/jam.jsonl
./braid -C fixtures/trees/cli-orig fixtures/cli-pr7.json
gh api repos/cli/cli/pulls/7/comments | ./braid -C /path/to/cli
```

Python 3.9+, stdlib. Exit 0 occupy-ok / empty, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v0.1 — compose then occupy the fold

`./braid --selftest` → **23 passed**. `./demo.sh` → **52 passed, 0 failed**.

Gold plait `fixtures/commute.jsonl` against `alpha/beta/gamma`:

```
braid  n=2  files=1  compose=PARALLEL  occupy=PENDING
  COMMUTE  app.py  #alice@1  #bob@3  disjoint spans
  PENDING    app.py  union-before  before_hits=2 after_hits=0
# rc=0
```

One composed claim (`#alice,#bob`). Not two PENDING rows.

Same stream, tree `ALPHA/beta/gamma` (A already applied):

```
occupy=SUPERSEDED  method=union-neither  note=partial apply of the composed image
```

plea would be APPLIED + PENDING. braid is SUPERSEDED of the union. Tree `ALPHA/beta/GAMMA` is APPLIED.

Gold `jam.jsonl`: `compose=JAMMED occupy=—` rc=2, JSON `occupied=false composed=[]`. Split same-span two afters rc=1, also no occupy. Overlapping ranges whose join line agrees (`SHARED`) still JAM — replacement, not hunk-union.

STACK `beta→beta2→beta3` (inverted `created_at`):

| tree | occupy |
| --- | --- |
| `beta` | PENDING of the fold `beta→beta3` |
| `beta3` | APPLIED |
| `beta2` | SUPERSEDED (neither origin nor final) |
| `beta` and `beta2` live | PENDING (origin still there; not APPLIED of the wrong tree) |

plait's inverted-clock `same-tree` on `alpha,beta2,beta3` is not the object. Occupancy is of the series after-image.

ECHO same locus collapses to one part. Same `return 0→return 1` on line 1 *and* line 10 is COMMUTE (two loci) and occupies the two-site union; applying one site is SUPERSEDED of that union.

Markdown without a quote fence: `before=None recon=none`, disjoint afters COMMUTE, not SPLIT on `[]==[]`. cli/cli PR #7 `#333030758,#333031216` one PARALLEL occupancy PENDING against the orig snapshot (`return nil, err` elsewhere in the file is not a hit: locus slack).

Empty stdin rc=0. Binary stdin / junk JSONL line rc=3 (not EMPTY, not SPLIT). A↔B cycle JAM rc=2. Insert-then-edit (`pass` → function, then `return 1→2`) SERIES-folds to `return 2` and occupies that image.

### v0.2 — covering is the file after-image; empty before occupies the after

Forced by the v0.1 commute run, not a feature list:

1. **Gap fill.** alice@1 × bob@3 cannot paint a covering from strand befores (beta is unclaimed). v0.1 occupied the concatenation `alpha|gamma → ALPHA|GAMMA` (`union-before`). The tree still holds `beta`. v0.2 fills unclaimed lines from the tree, then applies the strands onto that canvas. The composed claim is the file region:

```
$ ./braid --json -C fixtures/trees/commute fixtures/commute.jsonl
covering=true  before=['alpha','beta','gamma']  after=['ALPHA','beta','GAMMA']
occupy=PENDING  method=exact-before
```

A-only (`ALPHA/beta/gamma`) is still SUPERSEDED (`covering-neither`) of that region, not APPLIED+PENDING. Insert+edit (`shift.jsonl`) paints `a,b,c,d → a,a2,b,c,D`. Two-site ECHO-that-is-COMMUTE paints the whole 10-line after-image.

2. **Markdown without a quote fence.** v0.1 compose was correctly PARALLEL; occupancy against `alpha/beta/gamma` was SUPERSEDED because empty befores made every leftover-before flag false. The composed after-image is not in the tree. With covering fill, the same stream occupies **PENDING exact-before** of `ALPHA, beta, GAMMA` — occupancy of the after, not a fake SUPERSEDED.

`./braid --selftest` → **25 passed**. `./demo.sh` → **57 passed, 0 failed**.

## Dogfood targets

- plait gold `fixtures/commute.jsonl` / `jam.jsonl` (copied; also the plait worktree and `/tmp/destroy-plait/` when present)
- DESTROYER_PLAIT fixtures: echo-dup-sites, md-commute-noquote, stack-cycle, stack-subset, same-line-overlap-same-after, same-line-split
- cli/cli PR #7 harvest + `fixtures/trees/cli-orig/command/pr.go`
- Synthetic occupancy trees: commute, commute-a-only, commute-applied, stack, stack-mid, stack-after, stack-both, dup-sites

## Surprises

- Locus slack is load-bearing on cli/cli #333030758: `\t\treturn nil, err` already exists seven lines below the comment. File-wide after-search would stain the union. Occupancy of the composed claim still needs a locus, or the union lies.
- STACK with both images live (`beta` and `beta2`) is PENDING of the fold, not SUPERSEDED: the origin before is still in the tree. The lie to avoid is APPLIED of `beta3` when `beta3` is absent. PENDING is honest.
- Filling a COMMUTE gap from the *current* tree mixes the original snapshot (strand befores) with live context. A-only still SUPERSEDED because claimed lines stay as strand befores (`alpha`, not the live `ALPHA`). That mix is the composed file region, and it is why v0.2 occupancy is `exact-before` of three lines instead of a concatenation.
- cli/cli #333030758×#333031216 covering is the 54-line span between @347 and @400, PENDING `exact-before` against orig. Drift anywhere in that window would SUPERSEDE the covering even if both nits were still open — stricter than the v0.1 union of two return lines. Locus on parts remains the fallback when covering cannot apply.

## Failures

- `--remarks` on cli-pr7 is MIXED (PARALLEL + THREAD components). Occupy of the suggestion plait stays PENDING; remarks are not after-images. Fine, but the header `compose=MIXED` is noisier than plait's split listing.
- No `--emit` of the composed patch. Occupancy is the verb.
- SERIES still occupies the one-line fold (`beta→beta3`), not a file covering: the two rounds disagree on the claimed line, so paint refuses. stack-both stays PENDING of the origin, not SUPERSEDED of a file snapshot.

## Suggested mutations

- `--emit` the composed covering as a unified diff (spar `--lock` was this hybrid).
- Multi-file COMMUTE as one tree-image occupancy (currently one composed claim per path, unanimous fate).
- NFC-equivalent path keys so APFS `café.py` / `café.py` commute instead of two PARALLEL singletons.

## Kill / keep

**Keep.** The object changed. Demo case 3 is a tree on which sate/plea print two rows (APPLIED + PENDING) and braid prints one SUPERSEDED of the union. Demo case 6 is a STACK mid-state on which occupying each round says APPLIED of round 1, and braid says SUPERSEDED of `beta→beta3`. JAM still refuses to occupy. DESTROYER_PLAIT's ECHO-as-image, empty-before SPLIT, replacement-as-union, and inverted-clock same-tree are not reproduced.

Kill only if a later generation proves that `plait; sate` plus a hand-written fold recovers the SUPERSEDED-of-union fate — it does not, because discovering that the tree occupies *neither* the composed before *nor* the composed after is the object.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | braid -C HEAD` is the interaction: compose, then one occupancy.
- Partial apply of a commuting pair is SUPERSEDED of the composed image.
- STACK occupancy is of the series fold; leftover `beta2` is not APPLIED of round 1.
- JAM/SPLIT still fail closed without a fake occupancy.
- Locus-aware ECHO: two identical nits on two lines commute and occupy twice.

**Lost**

- plait's apply-schedule witness table (`line`/`time`/`topo`/`same-tree`). The fold is the witness.
- sate `--log` of historical patches. Pipe a stream in.
- spar `--emit` / `--all-commits` harvest grouping. Pairwise still within `original_commit_id` for STACK; COMMUTE of disjoint spans does not require a shared commit.
