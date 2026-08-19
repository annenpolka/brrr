# DESTROYER — braid

Adversarial pass on occupancy of the **single composed after-image**. No rewrites: the failures are conceptual, not one-line bugs. DESTROYER_PLAIT already named COMMUTE / JAM / ECHO-as-image / empty-before SPLIT / replacement-as-union / inverted-clock `same-tree`. Those are not re-run as plait's schedule table. The object here is whether braid occupies *that* fold.

- **braid** (hybrid-12, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cbac00204512`
- Peels (not the target): **hank** `--emit` (`mutation-87`), **quire** tree-image emit (`mutation-97`)
- Contrast occupancy: **plea** (`mutation-24`) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b0f-7ef0-76c0-9975-2d17551b311f`
- Transcript: `/tmp/destroy-braid/transcript.txt`
- Follow-up: `/tmp/destroy-braid/followup.txt`
- Fixtures: `/tmp/destroy-braid/fixtures/`
- Trees: `/tmp/destroy-braid/trees/`
- Attack driver: `/tmp/destroy-braid/attack.py`
- `./braid --selftest` → `selftest 25/25 passed` after the attacks. `./demo.sh` → `PASS=57 FAIL=0`. `braid 0.2.0`.

Attacks: STACK mid-state (plea APPLIED-of-round-1 vs braid SUPERSEDED-of-`beta3`), three-round STACK that cannot occupy, covering window drift (gap fill vs chimera), NFC `café` paths and line images, `--remarks` MIXED/COVER, no `--emit` (hank), empty-before occupy of a live canvas, replacement-as-union refuse, inverted-clock with no `same-tree` table.

Verdict: **mutate, do not kill.** Occupancy of the fold is still a real verb. Demo case 6 is a tree on which plea prints APPLIED of round 1 + PENDING of round 2, and braid prints one SUPERSEDED of `beta→beta3`. Gold JAM still refuses to occupy. DESTROYER_PLAIT's inverted-clock `same-tree` of the wrong image is not reproduced. The attacks show where a three-round series is SPLIT (no occupy), where covering occupancy is of a live-gap canvas rather than of the nits, and where NFC line images miss.

---

## Primitive restated

Compose review-suggestion strands first (refuse on JAM/SPLIT), then occupy the **single composed after-image** against a tree — one occupancy of the union/fold, not N strand rows. Exit 0 occupy-ok / empty, 1 SPLIT, 2 JAMMED, 3 error. Not plait's `line`/`time`/`topo`/`same-tree` table. Not hank `--emit`.

Cited from DESTROYER_PLAIT (do not re-litigate as schedule witnesses):

- §1 replacement is the object; "same after" is not hunk-union.
- §2 inverted timestamps + both-images reported `same-tree` on `alpha,beta2,beta3`, not the SERIES fold.
- §3 markdown without a quote fence minted `before=[]` and SPLIT disjoint afters.
- §6 NFC path vs NFD path were two PARALLEL singletons on one APFS inode.
- §8 ECHO-as-image (same before→after on two loci) — braid already locussed this; not re-run wholesale.

---

## 1. STACK mid-state — SUPERSEDED of `beta→beta3` is the object; three rounds cannot occupy it (survived / conceptual, load-bearing)

Gold two-round STACK, inverted `created_at` (victim `fixtures/stack.jsonl`):

| tree | braid occupy of `beta→beta3` | plea of the strands |
| --- | --- | --- |
| `alpha/beta/gamma` (origin) | **PENDING** `exact-before` | PENDING round1 + SUPERSEDED round2 (`unanimous=SPLIT`) |
| `alpha/beta2/gamma` (**mid**) | **SUPERSEDED** `covering-neither` | **APPLIED round1 + PENDING round2** |
| `alpha/beta3/gamma` (fold) | **APPLIED** `exact-after` | SUPERSEDED round1 + APPLIED round2 |
| `alpha/beta/beta2/gamma` (both live) | **PENDING** `exact-before` | DUPLEX round1 + PENDING round2 |

```
$ ./braid --json -C fixtures/trees/stack-mid fixtures/stack.jsonl
compose=SERIES occupy=SUPERSEDED method=covering-neither
  before=['beta'] after=['beta3']   covering @2

$ ./plea --json --worktree -C fixtures/trees/stack-mid fixtures/stack.jsonl
unanimous=SPLIT  counts={APPLIED: 1, PENDING: 1}
  round1 APPLIED exact-after   # beta2 is taken
  round2 PENDING exact-before  # leftover mid-image
```

That is the primitive. Concatenating `plait | plea` cannot say SUPERSEDED of the composed image when only round 1 has landed. Do not kill.

**Both images live is PENDING of a 1-line origin.** SERIES covering is `@2` `beta → beta3`, not a file region. `alpha`/`gamma` (and leftover `beta2`) are invisible. Neighbor drift `ALPHA/beta/GAMMA` stays PENDING of the fold. Honest about `beta3` absent; a lie about the leftover mid-image still sitting on disk. CANDIDATE already named "SERIES still occupies the one-line fold… stack-both stays PENDING of the origin, not SUPERSEDED of a file snapshot." Confirmed, not closed.

**Three-round `v1→v2→v3→v4` (inverted clocks) is SPLIT, occupy refused:**

```
$ ./braid --json /tmp/destroy-braid/fixtures/stack-three.jsonl
compose=SPLIT occupy=None occupied=False  rc=1
  STACK r1×r2  after(a)==before(b)
  STACK r2×r3  after(a)==before(b)
  SPLIT r1×r3  same span, two afters     # v2 vs v4
```

plait on the same stream (DESTROYER_PLAIT's algebra, not occupancy):

```
$ ./plait /tmp/destroy-braid/fixtures/stack-three.jsonl
  COMMUTE  app.py  #r1@2  #r3@2  distinct commits; images independent
  STACK    … r1×r2   STACK … r2×r3
  SERIES   app.py  #r1,#r2,#r3  unique apply order
# rc=0
```

Braid inherited plait's STACK chain and then **SPLIT-gated occupancy** on the non-adjacent same-span pair. `component_verdict` hits SPLIT before SERIES. Mid-state `v2` (plea: APPLIED r1 + PENDING r2 + SUPERSEDED r3) cannot be asked "does HEAD occupy `v1→v4`?" — the fold is unaskable. Two-round gold survives because there is no non-adjacent pair.

Insert-then-edit subset (two strands, STACK via `b.before lives in a.after`) still occupies the series: origin PENDING of `pass → return 2`; mid (`return 1` live) SUPERSEDED of that fold; plea mid is APPLIED insert + PENDING edit. Same money shot, two rounds only.

---

## 2. Covering window drift — gap fill absorbs content; position shift mints a chimera (conceptual, load-bearing)

v0.2 covering paints claimed lines from strand befores and **fills unclaimed gaps from the current tree**, then occupies that file region.

**Unclaimed-gap content drift is PENDING of a live canvas, not SUPERSEDED of the review snapshot.**

```
$ ./braid -C trees/window-drift-mid fixtures/window-commute.jsonl
composed  alpha | BETA | gamma  →  ALPHA | BETA | GAMMA
occupy=PENDING  exact-before
# tree is alpha/BETA/gamma; both nits still open
```

CANDIDATE surprises said: "Drift anywhere in that window would SUPERSEDE the covering even if both nits were still open — stricter than the v0.1 union of two return lines." Empirical: the gap is filled from HEAD, so the covering *is* the drifted file. Occupancy of the nits cannot see that `beta` moved on.

Same on a 12-line distant COMMUTE (`L1`×`L12`): drift of `L6` is painted into both before and after; occupy PENDING. cli/cli PR #7 covering is 54 lines `@347-400`. Changing the unclaimed TODO at line 363 (`figure out a less ridiculous way…` → `drifted comment inside the covering window`) stays PENDING `exact-before`. Both return-nil nits still live.

Sitbone `PresenceArbiter.swift` (no ` ```suggestion ` in the repo; synthetic commute `@9`×`@14`): covering is the 6-line span. Drifting the ADR comment at line 11 paints `// window-drift` into the composed before **and** after. occupy PENDING of that mixed region.

**Position shift of one line SUPERSEDES even though both nits are still in the file.** Pad above the 3-line commute:

```
tree = PAD / alpha / beta / gamma
composed  alpha | alpha | gamma  →  ALPHA | alpha | GAMMA
occupy=SUPERSEDED  covering-neither
```

Claimed `alpha` stays pinned at line 1; the gap fills from the shifted tree (`alpha` now at line 2). The covering is a chimera that exists nowhere. `far-shift1` (PAD + `L1…L12`) is the same object: before `['L1','L1','L2',…,'L10','L12']`, SUPERSEDED, while `L1` and `L12` still sit on disk.

So covering occupancy is neither "stricter window" nor "locus of the nits." It is exact match of a snapshot/live mix:

| drift | occupy | why |
| --- | --- | --- |
| unclaimed line content (`beta→BETA`, cli TODO, sitbone ADR) | **PENDING** | gap fill rewrites the claim to match HEAD |
| one-line pad / block shift | **SUPERSEDED** | chimera before-image |
| extra line *below* the window | PENDING | covering is still the prefix |
| trailing space on a *claimed* line | SUPERSEDED | occupy does not honor `--ignore-space` |
| duplex: origin block *and* after block live | DUPLEX `exact-both` | honest |

`--ignore-space` on `before=["alpha  "]` still paints `['alpha  ','beta','gamma']` and SUPERSEDES origin `alpha/beta/gamma`. Compose may collapse space; occupy of the covering does not.

STACK 1-line fold is the other invert: `LOCUS_SLACK=2` keeps `pad×2 + alpha/beta/gamma` PENDING of `beta→beta3`; `pad×3` is SUPERSEDED. Neighbors can freely drift.

---

## 3. NFC café paths — path key collapsed; line image is not NFC (conceptual)

Ingest NFC-normalizes `path`. DESTROYER_PLAIT §6's two PARALLEL singletons on one inode are not reproduced as two files:

```
$ ./braid --json nfc-two-paths.jsonl
strand paths: ['café.py', 'café.py']   files=1
# NFD cafe\u0301.py became NFC café.py; they COMMUTE as one covering
```

Against an NFC tree and against an NFD tree (APFS inodes 121470759 vs 121470761; each dir also sees the other name): occupy PENDING of `x, middle, p → y, middle, q`. Path key is fixed.

**Line images are raw.** NFC `café` vs tree NFD `café` (U+0065 U+0301):

```
nfc-content vs nfd-word  occupy=SUPERSEDED  covering-neither
nfd-content vs nfc-word  occupy=SUPERSEDED  covering-neither
matched normalization   occupy=PENDING
```

A reviewer who typed `café` and a tree that stored NFD (or git `core.precomposeunicode=false`) SUPERSEDES a still-open nit. Path NFC without image NFC is half the DESTROYER_PLAIT hole.

---

## 4. `--remarks` MIXED / COVER — occupy of the suggestion covering survives the header (conceptual)

cli/cli PR #7 with `--remarks`:

```
braid  n=7  files=2  compose=MIXED  occupy=PENDING
  COMMUTE  command/pr.go  #333030758@347  #333031216@400
  THREAD   context/context.go  (reply chains)
  PARALLEL command/pr.go  #333030758,#333031216  @347-400 covering
  PENDING  command/pr.go  exact-before
```

Remarks are not after-images (`compose_all` skips groups with no edit). Occupy of the suggestion plait stays PENDING. The header `compose=MIXED` is noisier than plait's split listing (CANDIDATE failures). Confirmed, not a false occupancy.

Same-file remark on alice's locus **COVER-absorbs the commute component**:

```
compose=COVER occupy=PENDING
  strands alice,nit,bob  pair_counts={COMMUTE:1, COVER:1, DISJOINT:1}
  covering still alpha,beta,gamma → ALPHA,beta,GAMMA
```

`component_verdict` hits COVER before PARALLEL. Occupancy of the fold is still the two nits. The compose label is the lie. DESTROYER_PLAIT §5's "COVER-on-replies still gone" / "one-file mixed 100 collapses to one COVER" is the same CONNECTING union, now sitting in front of one occupancy row.

---

## 5. No `--emit` — hank's verb; not a kill

```
$ ./braid --emit
unrecognized arguments: --emit
# rc=2  argparse
```

`--help` does not mention emit. hank on the same STACK stream emits `-beta` `+beta3` with `alpha`/`gamma` context (`hank --emit | git apply` of the fold). quire is the multi-file emit peel. Occupancy is the verb. Do not kill braid for missing stdout of a covering; that mutation already exists.

---

## 6. Empty-before SPLIT — disjoint COMMUTE survived; occupy paints the live canvas (survived / conceptual)

DESTROYER_PLAIT §3: markdown without a quote fence was `before=[]==[]` SPLIT of disjoint afters. Braid:

```
$ ./braid --json -C fixtures/trees/commute fixtures/md-commute-noquote.md
compose=PARALLEL  recon=none  occupy=PENDING
  covering  alpha,beta,gamma → ALPHA,beta,GAMMA
```

Disjoint empty-before is COMMUTE, not SPLIT. Gold. Same-line two empty afters (`HELLO world` vs `hello WORLD`) is SPLIT, occupy refused — replacement, not word-union (DESTROYER_PLAIT §1, occupancy-closed).

**Occupy of empty-before is occupancy of whatever HEAD is.** Tree `XXX/YYY/ZZZ`:

```
composed  XXX | YYY | ZZZ  →  ALPHA | YYY | GAMMA
occupy=PENDING  exact-before
```

No review snapshot is claimed. Tree already `ALPHA/beta/gamma` (alice landed): covering before becomes `ALPHA,beta,gamma`, after `ALPHA,beta,GAMMA` (bob still a span-replace because `s.before is None` applies at the span). PENDING of a no-op-on-alice canvas, not APPLIED of alice + PENDING of bob, and not SUPERSEDED of a union. Empty before occupies a live splice, not a composed after-image.

Create-file `before=[] after=["print(1)"]` with missing path: SUPERSEDED `missing-file`, not PENDING of an insert.

---

## 7. Replacement-as-union — occupy refused (survived)

DESTROYER_PLAIT §1, occupancy consequence only:

| stream | compose | occupy | rc |
| --- | --- | --- | --- |
| `hello world` → `HELLO world` × `hello WORLD` | SPLIT | — | 1 |
| same-line two afters (`split.jsonl`) | SPLIT | — | 1 |
| overlap same-join `SHARED` (`same-line-overlap-same-after.jsonl`) | JAMMED | — | 2 |
| gold `jam.jsonl` | JAMMED | — | 2 |

`composed=[]`. A union `HELLO WORLD` / `A,SHARED,C` is not occupied. Honest refuse. Not re-run as plait pair-algebra.

---

## 8. Inverted-clock same-tree — the fold is the witness (survived)

DESTROYER_PLAIT §2: both-images + inverted time reported `same-tree` on digest `alpha,beta2,beta3`. Braid has no apply-schedule table:

```
$ ./braid -C trees/stack-both invert-stack.jsonl
compose=SERIES occupy=PENDING
  STACK  after(a)==before(b)  a>b
  composed  beta → beta3
  PENDING  exact-before
# "same-tree" in output: False   "apply:line": False
```

Fold after-image is still `beta3` despite `created_at` round2 < round1. Mid-state SUPERSEDED of that fold. The plait lie is not reproduced. The leftover hole is §1's 1-line covering, not a clock.

---

## What survived

- Gold **STACK mid-state**: `stack-mid` is SUPERSEDED of `beta→beta3`; plea is APPLIED+PENDING of the rounds. Demo case 6. The object.
- Gold **COMMUTE covering**: `alpha/beta/gamma → ALPHA/beta/GAMMA` PENDING; a-only SUPERSEDED of the region, not APPLIED+PENDING.
- Gold **JAM/SPLIT refuse occupy**: `jam.jsonl` rc=2 `occupy=—`; replacement-as-union not occupied.
- Gold **cli/cli PR #7** `#333030758,#333031216` one PARALLEL covering `@347-400` PENDING against orig. Locus slack keeps leftover `return nil, err` at 354 from staining.
- **Inverted-clock** STACK still occupies `beta→beta3`. No `same-tree` of the wrong tree.
- **Empty-before disjoint** markdown is PARALLEL PENDING, not DESTROYER_PLAIT's SPLIT.
- **ECHO is a locus** (victim selftest `echo-is-locus-not-image`); not re-attacked.
- **NFC path key** collapses NFD→NFC (one file, not two PARALLEL singletons).
- Empty stdin / binary stdin / junk JSONL: already rc=0 / 3 / 3 in victim demo. Not re-run.
- `--selftest` 25/25. `./demo.sh` 57/57. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

Occupancy of the fold is not extinct. A developer who took round 1 of a stacked suggestion and asks "is the series done?" still gets SUPERSEDED of `beta3`, not APPLIED of `beta2`. JAM still fails closed. DESTROYER_PLAIT's `same-tree` lie is gone because the fold is the witness. Nothing in this battery turned that into `plea` of N rows or into `hank --emit`.

Do not kill because of three-round SPLIT, covering gap-fill, NFC line images, or MIXED remarks. Those are mutations. Killing them would throw away SUPERSEDED-of-the-union to hide a pair-order footgun.

| do not kill because | mutate toward |
| --- | --- |
| `stack-mid` SUPERSEDED of `beta→beta3` vs plea APPLIED+PENDING; a-only commute SUPERSEDED of the region; jam rc=2 `occupy=—`; cli #7 one covering PENDING; inverted-clock fold; empty-before disjoint COMMUTE | **Transitive STACK occupies the origin→final fold.** Non-adjacent same-span afters in a STACK chain must not SPLIT the component. Three-round `v1→v4` mid-state is currently unaskable. |
| | **Covering occupancy is of the nits, not of a live-gap canvas.** Unclaimed-line content drift (cli TODO, sitbone ADR, `beta→BETA`) must not rewrite the composed before to match HEAD. Position-shift chimeras (`alpha\|alpha\|gamma`) SUPERSEDE while both nits still live — occupy the parts (v0.1 union) when the covering cannot apply, or paint gaps from the *origin* snapshot. |
| | **SERIES covering is a file region, or leftover mid-images are visible.** `stack-both` PENDING of `@2` hides live `beta2`. CANDIDATE named this. |
| | **NFC-normalize line images**, not only path keys. `café` vs `café` is SUPERSEDED of a still-open nit. |
| | **`--ignore-space` must apply to occupy**, not only pair_verdict. Trailing space on a claimed before SUPERSEDES origin. |
| | **`--remarks` CONNECTING must not COVER-label the suggestion plait.** Occupy already skips remark-only groups; `compose=COVER`/`MIXED` is the header lie. |
| | Create-file / missing path: PENDING of an insert, not SUPERSEDED `missing-file`. Multi-file MIXED is quire's peel (tree-image), not a braid kill. `--emit` is hank. |

A one-line NFC on `before`/`after` would hide the café miss and would not touch three-round SPLIT or covering gap-fill. Not applied.

Do not grow a review platform. The next mutation is *occupancy of the series fold when N>2* plus *nit-locus covering* (gaps are context, not claim), not hank `--emit` and not plait's schedule table.
