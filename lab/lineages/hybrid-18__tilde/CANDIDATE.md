# hybrid-18 — tilde

## Primitive

Compose review-suggestion strands first (refuse on JAM/SPLIT), then occupy the **single composed after-image** against a tree using **NFC-equivalent path and line keys** — covering occupancy is of the nits, not a live-gap canvas.

## Why this might not exist

braid occupies the fold, but DESTROYER_BRAID §3 + §2 showed two holes in *that* occupancy: path keys collapse NFC/NFD while line images stay raw (`café` vs `café` SUPERSEDES a still-open nit), and covering paints unclaimed gaps from HEAD so gap-content drift is PENDING of a live canvas and a one-line pad mints a chimera `alpha|alpha|gamma`. hank `--emit`s the covering; it does not fix the keys. plea occupies each strand. Concatenating `plait | sate` cannot say SUPERSEDED of the union when only A has landed.

The reviewer question after "they commute" is occupancy of *that* result, with the same Unicode the filesystem uses, of the nits the reviewer claimed.

Discarded: a one-line NFC on `before`/`after` that would hide the café miss and leave the chimera; hank `--emit`; a fourth cinch; DESTROYER_PLAIT's schedule table.

## How to run

```bash
chmod +x ./tilde ./demo.sh
./tilde --help
./tilde --selftest
./demo.sh
./tilde -C fixtures/trees/commute fixtures/commute.jsonl
./tilde fixtures/jam.jsonl
./tilde -C fixtures/trees/stack-mid fixtures/stack.jsonl
./tilde --json fixtures/nfc-two-paths.jsonl
./tilde -C fixtures/trees/nfd-word fixtures/nfc-content.jsonl
./tilde -C fixtures/trees/window-drift-mid fixtures/window-commute.jsonl
./tilde -C fixtures/trees/cli-orig fixtures/cli-pr7.json
```

Python 3.9+, stdlib. Exit 0 occupy-ok / empty, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v0.1 — NFC keys; occupy the nits

`./tilde --selftest` → **27 passed**. `./demo.sh` → **73 passed, 0 failed**. `tilde 0.1.0`.

Gold braid `fixtures/commute.jsonl` against `alpha/beta/gamma`:

```
tilde  n=2  files=1  compose=PARALLEL  occupy=PENDING
  COMMUTE  app.py  #alice@1  #bob@3  disjoint spans
  composed  alpha | gamma  →  ALPHA | GAMMA
  PENDING    app.py  union-before
# covering=false  rc=0
```

One composed claim (`#alice,#bob`). The gap `beta` is not in the claim. braid v0.2 painted `alpha|beta|gamma` from HEAD.

Same stream, tree `ALPHA/beta/gamma` (A already applied): `occupy=SUPERSEDED`. Tree `ALPHA/beta/GAMMA` is APPLIED. plea would be APPLIED+PENDING.

Gold `jam.jsonl`: `compose=JAMMED occupy=—` rc=2, JSON `occupied=false composed=[]`.

STACK `beta→beta2→beta3` (inverted `created_at`), demo case 6:

| tree | occupy |
| --- | --- |
| `beta` | PENDING of the fold `beta→beta3` |
| `beta3` | APPLIED |
| `beta2` | **SUPERSEDED** (neither origin nor final) |
| `beta` and `beta2` live | PENDING (not APPLIED of the wrong tree) |

NFC café pair (`fixtures/nfc-two-paths.jsonl`): strand paths both `café.py`, `files=1`, one PARALLEL occupy. Against NFC tree and against NFD tree: PENDING.

NFC line vs NFD tree (`café` claim, `café` on disk): **PENDING** `exact-before`, not SUPERSEDED of a still-open nit.

Covering window:

| tree | occupy | why |
| --- | --- | --- |
| `alpha/BETA/gamma` | PENDING of `alpha\|gamma` | gap is not a claim |
| `PAD/alpha/beta/gamma` | PENDING | not SUPERSEDED of chimera `alpha\|alpha\|gamma` |
| `ALPHA/beta/gamma` | SUPERSEDED of the nits | partial apply |

cli/cli PR #7 `#333030758,#333031216` one PARALLEL occupancy PENDING of the two return-nil nits (not a 54-line live covering).

### v0.2 — occupy honors `--ignore-space`

Forced by v0.1: trailing space on a claimed before (`fixtures/ws-before.jsonl` `alpha  `) SUPERSEDED origin `alpha/beta/gamma` even though compose already collapsed space. DESTROYER_BRAID named this. Occupy of the nits now uses the same `_norm` as pair_verdict.

```
$ ./tilde --json -C fixtures/trees/commute fixtures/ws-before.jsonl
occupy=SUPERSEDED  method=union-neither

$ ./tilde --ignore-space --json -C fixtures/trees/commute fixtures/ws-before.jsonl
occupy=PENDING  method=union-before
```

STACK mid-state with `--ignore-space` is still SUPERSEDED of `beta→beta3`. JAM still refuses.

`./tilde --selftest` → **28 passed**. `./demo.sh` → **76 passed, 0 failed**. `tilde 0.2.0`.

## Dogfood targets

- braid gold: `fixtures/commute.jsonl` / `jam.jsonl` / `stack.jsonl` / `echo-dup-sites.jsonl` / `shift.jsonl` / `stack-subset.jsonl` / `md-commute-noquote.md` / `cli-pr7.json` + `fixtures/trees/cli-orig/command/pr.go`
- DESTROYER_BRAID café pair: `nfc-two-paths.jsonl`, `nfc-content.jsonl` × `nfd-word`, `nfd-content.jsonl` × `nfc-word`
- Covering window: `window-commute.jsonl` × `window-drift-mid` / `window-pad1` / `window-a-only`
- `--ignore-space` occupy: `ws-before.jsonl` × origin commute tree

## Surprises

- Occupancy of the nits recovers braid v0.1's SUPERSEDED-of-union on a-only *and* kills v0.2's chimera, without giving up SERIES SUPERSEDED of `beta→beta3`.
- Empty-before markdown against `XXX/YYY/ZZZ` is PENDING of the nits, not PENDING of a live splice of HEAD. braid painted HEAD into the covering.
- APFS lists `café.py` and `café.py` as the same inode in one directory; two trees (nfc-file vs nfd-file) still need NFC-equivalent path lookup so `-C` finds the file.

## Failures

- SERIES covering stays the 1-line fold; `stack-both` PENDING hides live `beta2`.
- `--remarks` CONNECTING can still COVER-label a suggestion plait. Occupy skips remark-only groups.
- No `--emit` of the covering. That is hank.
- Three-round STACK is still SPLIT (non-adjacent same-span afters). Not this mutation.

## Suggested mutations

- Transitive STACK occupies the origin→final fold when N>2 (non-adjacent same-span afters must not SPLIT).
- SERIES leftover mid-images visible, or SERIES covering is a file region.
- `--remarks` CONNECTING must not COVER-label the suggestion plait.

## Kill / keep

**Keep.** Demo case 6 is still SUPERSEDED of `beta→beta3`. JAM still refuses. NFC commute is one occupy. Covering is not a chimera.

Kill only if occupying each strand plus a hand-written NFC fold recovers SUPERSEDED-of-union — it does not, because discovering that the tree occupies *neither* the composed before *nor* the composed after is the object, and the chimera was that object lying.

## What the flipped assumption bought and lost

**Bought**

- `gh api …/comments | tilde -C HEAD` occupies the fold with filesystem Unicode.
- Partial apply is still SUPERSEDED of the composed image.
- Unclaimed-line drift and pad-shift no longer rewrite or SUPERSEDE the claim.
- `--ignore-space` occupy of a claimed before (v0.2).
- JAM/SPLIT still fail closed.

**Lost**

- braid v0.2's file-region covering (`alpha|beta|gamma → ALPHA|beta|GAMMA`) as the occupy object. Gaps are context.
- hank `--emit`. Occupancy is the verb.
- plait's apply-schedule witness table. The fold is the witness.
