# candidate-33 — tide

## Primitive

A test oracle is a claim with a career: tide extracts expected-value
literals (and expected-* JSON leaves), aligns them across git history by
(path, test, lhs), and classifies the series.

## Four primitives considered

1. **gloss** — Review comments as claims on a locus; IGNORE / RETORT / VACATE
   against later trees. **Discarded:** relocation is slip-adjacent; without a
   local comment corpus the object is GitHub-shaped, not a Unix object.
2. **kerf** — A diff hunk as an object; LIVE / REVERTED / PARTIAL / DRIFTED
   against a tree. **Discarded (parked):** `git patch-id` / `cherry` /
   `range-diff` occupy exact match; PARTIAL/DRIFTED is the novelty but needs
   a hunk file format. Suggested mutation, not v0.
3. **tide** — Oracle values as a time series. **Implemented.**
4. **chorus** — Cluster review comments by hunk identity across rebases, not
   thread id. **Discarded:** GitHub-API clustering; kerf's object in disguise.

`gloss` and `chorus` need review-comment identity that this worktree does
not have. `kerf` is real but closer to existing git verbs. tide's object
(the expected value) is not kiln's generation lot, not alibi's splice, not
held's boolean occupancy.

## Why this might not exist

`git log -L` follows a *line*. Coverage says a line *ran*. Mutation testing
perturbs operators. Snapshot `--update` rewrites goldens without a career.
CI says pass/fail. Nobody asks: *what did this test claim, and when did the
claim move?*

The recurring cheat is silent: a test goes green because the expected value
was edited. assertion-descent calls this out in prose ("do not change
expected test values merely to match the implementation"). tide is that
anti-cheat as archaeology.

## How to run

From the worktree root:

```bash
./demo.sh
./demo.sh 0
./tide --selftest
./tide --help
./tide -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --kind inline
./tide -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi --kind json
./tide -C /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
```

Python 3.9+, stdlib, `git`. `./tide` is the CLI.

## Empirical transcript

### v0.1 — naive JSON, no generated filter, versions as strings

`./tide --selftest` 28/28. unittest 8/8. Fixture demo: FLIPFLOP retries
3→5→3, RATCHET limit 1→2→4, RATCHET,BLESS timeout 30→60→120 (the 60 step
touched only the test file), golden damage 100→200 COUPLED.

Real repos:

- **kizu** — 1 changed oracle, the money shot:
  `hits[0].message` `"real scar outside fence -->"` → `"real scar outside fence"`
  (parser stopped capturing `-->`; the test's vow moved with production).
- **tenaoshi** — `$.expected_properties.max_length_ratio` 0.95→0.99, plus
  **noise**: `$.input` and `$.desc` DRIFT. Stimulus and commentary were
  treated as oracles.
- **voidtrace** — 352 shown. `engineVersion` `"0.19.0"→…→"0.22.0"` classified
  **DRIFT** (string, not number). Firehose of
  `packages/spec-artifacts/src/conformance/engine.generated.json`
  `$.activeClauses[10].guarantee` FLIPFLOP — generated array indices, not claims.
- **sitbone** — 199 oracles at HEAD, 0 changed. Honest: the vows never moved.

`it.each` in voidtrace crashed v0.1 (`enclosing_test` IndexError). Fixed
before calling the walk done.

### v0.2 — after dogfood (one improvement)

The object is the *expected claim*, not the stimulus and not a generated
projection.

- Default `--json-mode roots`: only `expectation` / `expected_*` subtrees.
  `--json-mode naive` still sees `input` (the v0.1 surprise, kept as a flag).
- Skip `*.generated.*` and `/generated/` paths.
- Dotted version strings ratchet.
- VANISH: a key that disappeared without mutating (tenaoshi dropped
  `max_diff_ratio` 0.6).

After:

- Fixture porcelain no longer lists `$.input`. Naive mode still does.
- tenaoshi: 2 oracles — `$.max_length_ratio` RATCHET 0.95→0.99, and
  `$.max_diff_ratio` VANISH 0.6. Input/desc gone.
- voidtrace: 352 → 61. `engineVersion` **RATCHET**. `loaded.snapshot.rules`
  5→6→7→9→11→16 RATCHET. One real FLIPFLOP: decision `sequence`
  `[0,1,2,3,4,5]→[0,1,2,3,4]→[0,1,2,3,4,5]`.
- kizu scar-message DRIFT unchanged.

`./demo.sh 0` exit 0.

## Dogfood targets

- Synthetic fixture in `demo.sh` (FLIPFLOP / RATCHET / BLESS / golden / testcase).
- `tests/test_tide.py` (extract + classify + mini git walk).
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,voidtrace,tenaoshi,sitbone}`.

## Surprises

- Two numeric values are always a RATCHET (any pair is monotonic). TIMEOUT
  30→60→120 is RATCHET,BLESS, not DRIFT. DRIFT of numbers needs a turn
  (1→3→2).
- Mixed commits hide BLESS: tenaoshi's 0.95→0.99 lived in
  "契約テスト全緑を達成" which also touched production, so the relaxation
  is COUPLED. The fixture's test-only commit is the clean BLESS.
- sitbone's 0 changed oracles is a result, not a miss: 199 STABLE vows.
- kizu `AgentKind::from_str("claude")` VANISH after a FromStr rewrite —
  the lhs identity died even though the expected enum did not.

## Failures

- Method-call lhs identity does not survive `from_str` → `.parse()` (VANISH
  + a new key). No RESHAPE class yet.
- `toEqual(someFixture.field)` is skipped (not a literal). The real oracle
  lives in the JSON file; that is correct, but easy to misread as "no test".
- `--check` cannot see BLESS inside a mixed production commit (per-path
  BLESS would).
- Baseline of the walk window is the parent of the oldest sampled commit,
  not the true natal commit of an oracle older than `--walk`.

## Suggested mutations

- **kerf** — hunk-as-object, the discarded sibling.
- **RESHAPE** — same test, same rank, new lhs, same/similar value.
- **per-path BLESS** — oracle file changed, the imported production module
  did not, even if the commit touched other prod files.
- `tide given` — pin an oracle key and fail CI if it ratchets without a
  tagged "oracle-intent" trailer.
- JSON-path identity by sibling `id` instead of array index.

## Kill / keep

**Keep.** The object is new, the kizu/tenaoshi/voidtrace transcripts are
real, and v0.2 is a measured narrowing rather than a feature pile.
