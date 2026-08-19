# mutation-64 — wale

## Primitive

ECHO is a **locus** (span ∩ image), not image-identity: same before→after at two sites is two strands, not apply-once.

## Why this might not exist

plait (candidate-38) is the composition algebra of review suggestions. DESTROYER_PLAIT showed COMMUTE and JAM are real, then killed ECHO as a concept: `return 0` at L1 and L10 collapsed to ECHO and applied only `['site1']`. Image-equality ran before spans. Empty markdown `before=[]` was a universal key, so disjoint ALPHA/GAMMA became SPLIT. The missing verb is the same algebra with ECHO bound to a place.

## How to run

From the worktree root:

```bash
chmod +x ./wale ./demo.sh
./wale --help
./wale --selftest
./demo.sh
./wale fixtures/commute.jsonl
./wale fixtures/jam.jsonl
./wale fixtures/cli-pr7.json
./wale -C /tmp/t fixtures/echo-dup-sites.jsonl
./wale fixtures/md-commute-noquote.md
```

Python 3.10+, stdlib. Exit 0 composable, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v0.1 (locus-aware ECHO; image-identity cannot outrank disjoint spans)

`./wale --selftest` → 28/28 (ancestor 23 plus locus / two-site apply / empty-before).

Gold re-run against ancestor plait, then matched:

| fixture | ancestor | wale |
| --- | --- | --- |
| `fixtures/commute.jsonl` | COMMUTE PARALLEL rc=0 | same |
| `fixtures/jam.jsonl` | JAM JAMMED rc=2 | same |
| `fixtures/cli-pr7.json` | `#333030758,#333031216` COMMUTE PARALLEL rc=0 | same |

Destroyer cases that change:

```
# ancestor
ECHO     app.py  #site1@1  #site2@10  same before→after
         apply order=['site1']  leftover L10 = return 0

# wale v0.1
COMMUTE  app.py  #site1@1  #site2@10  same image, distinct loci
         apply order includes site1 and site2
         digest 8ebc1b8f61f9 = return 1 × both sites
```

```
# ancestor md-commute-noquote.md
SPLIT    app.py  @1  @3  same before, two afters   rc=1

# wale v0.1
COMMUTE  app.py  @1  @3  disjoint spans            rc=0
# JSON of the same edits (json-commute.jsonl) is also COMMUTE
```

Same-locus ECHO (`echo.jsonl`) still apply-once `['alice']`. STACK / JAM / SPLIT-at-one-line unchanged.

### v0.2 (from DESTROYER_PLAIT §8 + §3)

The destroyer transcript named the hole as *apply-once is right on one locus, lethal on two*, and offered a named MULTI. v0.1 already applied both sites but called it COMMUTE / PARALLEL "independent" — the same word as alice/bob's different edits. That hid the flipped assumption.

Re-ran `/tmp/destroy-plait/fixtures/echo-dup-sites.jsonl` against `trees/dup-sites` after naming MULTI:

```
wale  n=2  files=1  components=1  MULTI=1

pairs
  MULTI    app.py  #site1@1  #site2@10  same image, distinct loci

wales
  MULTI    app.py  #site1,#site2  same image, distinct loci; apply each
          apply:line=ok,time=ok,topo=ok same-tree  applied=[site2,site1]
```

Pretty now prints `applied=[…]` so an ECHO cannot hide `['site1']` behind `apply:ok`. Digest still `8ebc1b8f61f9` (both `return 1`), not ancestor leftover `4fad3e4d4674`.

An echoed nit at L1 *plus* the same image at L10 is MULTI (apply each locus, collapse the L1 clique), not file-wide ECHO.

Markdown empty-before (`recon=none`) of ALPHA@1 / GAMMA@3 still COMMUTE, applies same-tree against `alpha/beta/gamma`. Quoted markdown and `json-commute.jsonl` stay COMMUTE. Same-line `md-split.md` stays SPLIT rc=1.

`./wale --selftest` → 30/30. `./demo.sh` → PASS=30 FAIL=0. Gold ancestor commute rc=0, jam rc=2, PR#7 `#333030758,#333031216` COMMUTE.

## Dogfood targets

- Gold: `fixtures/{commute,jam,echo,split,stack,subsume,shift,stream.md,cli-pr7.json,cli-cli-comments.json}`
- Destroyer: `fixtures/{echo-dup-sites,md-commute-noquote.md,md-commute-quoted.md,md-split.md,json-commute.jsonl}`
- `/tmp/destroy-plait/transcript.txt` (do not paper over)

## Surprises

- The markdown SPLIT was the *same* hole as duplicate-site ECHO: image-equality before spans. One flip (ECHO is a locus) fixes both.
- Empty `before=[]` with `recon=none` is not needed for the disjoint case if spans are checked first; it is needed so `[] == []` cannot SPLIT two missing images that happen to overlap by accident of default span=1. Same-span unquoted different afters still SPLIT (locus disagreement).
- Unique-image apply of `return 0` is `ambiguous-before x2`. Span apply is why two sites succeed. ECHO collapse was hiding that.

## Failures

- C(n,2) MULTI/COMMUTE pretty-print of 100 nits is still a firehose (not this mutation).
- STACK subset / cycle / same-tree-on-wrong-tree are still ancestor holes.
- NFC path vs NFD path still two files. Binary stdin still traceback rc=1 (destroyer left those unpatched on purpose).

## Suggested mutations

- STACK = "B applies only after A", not only `after(A)==before(B)`.
- Schedules that agree on the wrong tree are not `same-tree`.
- Hide or summarize C(n,2) MULTI/COMMUTE the way DISJOINT is hidden.

## Kill / keep

**Keep.** Gold COMMUTE/JAM/PR#7 still hold. The destroyer's lethal ECHO case is now MULTI with `applied=[site2,site1]`. Do not kill COMMUTE/JAM.
