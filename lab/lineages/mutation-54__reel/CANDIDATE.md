# mutation-54 — reel

## Primitive

A mixed commit is a coil: **reel emits the name-closed acts as a
`git format-patch` mailbox**, not a plot report. `git am` is the consumer.
`--check` still exits 1 on SPOIL/TANGLE.

## Four primitives considered

Ancestor **canto** (candidate-39) already had the plot: PRELUDE / PAYOFF /
ASIDE / SPOIL as a reading-order report, with `--split DIR` as an afterthought
that wrote `# comment` + `git diff` files for `git apply`. The mutation is
the default verb, not a new graph:

1. **reel** — format-patch mailbox of those acts. **Implemented.**
2. **canto --tdd** — PAYOFF first (red) then PRELUDE (green). Parked: that
   is chronological TDD, a different order object.
3. **per-track series** (`track-1/0001-…`, `track-2/0001-…`) as two stacked
   PRs. Parked as a mutation of reel: `git am` is linear.
4. **hunk-grain emit** (unsquash in-file `#[test]`). Discarded: still needs
   a formatter; file grain is what a patch series can name.

Not leftover names. Not inverse-printf. Not occupancy. The cheat reel names
is silent: a report you must still `git add -p` by hand, or a `--split` that
is not `git am`.

## Why this might not exist

Reviewers of a 14-file squash want the *commits that should have been*,
piped into `git am`, not a porcelain story they retype. `git format-patch`
only walks commits that already exist. `git add -p` asks you to choose
hunks. canto computed the required reading order and then *described* it.
The missing Unix object is the mailbox.

## How to run

From the worktree root:

```bash
./demo.sh 0
./reel --selftest
./reel --help
./reel -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone e9b0f75
./reel -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone -o /tmp/story --verify e9b0f75
./reel -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --check 04adde1
./reel -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --report --grain file 04adde1
git diff A B | ./reel --stdin --check
```

Python 3.9+, stdlib, `git`. `./reel` is the CLI.

## Empirical transcript

### v0.1 — default emit is the mailbox

`./reel --selftest` 33/33. `python3 -m unittest discover -s tests` 18/18.

Fixture squash (Lexer, Parser, tests, util, README):

```
$ ./reel -C "$FIX" $C0 $HEAD
From 0000000… Mon Sep 17 00:00:00 2001
From: reel <reel@demo>
Subject: [PATCH 1/5] PRELUDE: lexer.py
…
Subject: [PATCH 2/5] PRELUDE: parse.py
Subject: [PATCH 3/5] SOLO: util.py
Subject: [PATCH 4/5] PAYOFF: test_parse.py
Subject: [PATCH 5/5] ASIDE: README.md
```

No `reel N acts` porcelain. `--report` still names the plot.
`--against` three story commits: **mean_jaccard=1.0**.
`-o DIR --verify` **git am** reconstitutes TO (no APPLY.txt).
`--check` 0 on the clean squash. stdin Widget prod+test: `--check` exits 1.

Real repos:

- **sitbone `e9b0f75`** (dual-threshold hysteresis) — mailbox, not five
  prelude hunks:
  ```
  Subject: [PATCH 1/3] PRELUDE: PresenceArbiter.swift
  Subject: [PATCH 2/3] ASIDE: PresenceArbiterTests.swift
  Subject: [PATCH 3/3] PAYOFF: PresenceHysteresisTests.swift
  ```
  `--check` 0. `--verify` git am on `e9b0f75^` reconstitutes the tree.
  The money shot is almost: a **blank-line sibling** is its own commit
  *between* the impl and the tests. `git log` after am is not the story.

- **kizu `04adde1`** — `--report`: Cargo.lock / README / SPEC are ASIDE.
  `--check` exits **1** because `src/highlight.rs` and `src/hook/tests.rs`
  are SPOIL. Emit would still write patches (honest: cannot unsquash
  in-file `#[test]`).

- **kizu `edf2de9`** — `[PATCH 3/5] PRELUDE: types.rs` before
  `[PATCH 4/5] PRELUDE: revert.rs`. plans ASIDE.

- **tenaoshi `4878b75`** — 9 patches, mostly ASIDE (oracle-value tweak).
  Narrative-empty is a result.

`./demo.sh 0` exit 0 (33 selftests, 18 unittests, 22 demo asserts).

### v0.2 — emit parks ASIDE last (one improvement)

v0.1's sitbone mailbox was PRELUDE / **ASIDE** / PAYOFF. `git am` made a
blank-line commit between the impl and the tests. The report can afford
middle asides (topo is honest). A patch series cannot: it is what
`git log` will say the story was.

Default `--aside last`: story acts keep their relative order; ASIDE
acts trail. `--report` is unchanged (topo). `--aside inline` restores
v0.1. Dropping the whitespace ASIDE was rejected: TO contains the
blank line, so `--verify` would miss.

After:

```
$ ./reel -C sitbone e9b0f75 | grep ^Subject
Subject: [PATCH 1/3] PRELUDE: PresenceArbiter.swift
Subject: [PATCH 2/3] PAYOFF: PresenceHysteresisTests.swift
Subject: [PATCH 3/3] ASIDE: PresenceArbiterTests.swift
```

`--verify` still reconstitutes `e9b0f75`. tenaoshi `4878b75` now emits
three SOLOs then six ASIDES (oracle JSON/docs), not interleaved.
kizu `edf2de9` plans stay last. Fixture `--against` still 1.0.

`--check` still 0 on sitbone, 1 on kizu `04adde1` (SPOIL).

`./demo.sh 0` exit 0.

## Dogfood targets

- Synthetic fixture in `demo.sh` (Lexer/Parser/tests + util track + README
  aside; squash recovery; git-am verify; spoil --check).
- `tests/test_reel.py`.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi}`.

## Surprises

- File clustering would have put PresenceArbiter.swift + both test files
  in one patch. Name-closure puts only the test that *uses* PresenceArbiter
  in PAYOFF; the blank-line sibling is ASIDE — and in v0.1 that ASIDE
  **interrupted the series**. Emit order is now a different object from
  report order. `--report` still shows `#2 ASIDE` between prelude and
  payoff; the mailbox does not.
- `--against` on already-split kizu history is type-flow, not author
  boundaries. The fixture (Lexer then Parser then tests) scores 1.0.
- Default stdout is composable (`| git am`) and dangerous to `git am` into
  the wrong repo. `-o DIR --verify` is the safe form.
- kizu `mod js_ts` is a prelude; the e2e test did not cite `JsTsDialect`
  so it is not PAYOFF. Gaze that lives only in strings is invisible.

## Failures

- Whitespace ASIDE still occupies a trailing commit. `--drop-aside` would
  lie about TO. Folding all asides into one leftover patch is a mutation.
- `git.rs` PAYOFF of `read_file_at_revision` after the e2e prelude is
  backwards-looking: topo is correct given the edges.
- Common short natal names (`last`, `out`, `rel`) still mint defs.
- No compile-oracle: a name-closed act can still fail to typecheck.
- File-grain emit cannot unsquash in-file prod+test (Rust `mod tests`).
- `--stdin` cannot emit a mailbox (no FROM/TO blobs). Report/check only.

## Suggested mutations

- **per-track `-o DIR/track-N/`** — two features become two stacked PRs.
- **canto --tdd** — PAYOFF first.
- Module-root files (`mod foo`) count as definers of `foo`.
- `reel given` — fail CI if a PR range is a single SPOIL act.
- Cover letter on stdout as a commented prelude, not a `git am` empty commit.

## Kill / keep

**Keep.** The object is the **mailbox**, sitbone `e9b0f75` is a one-screen
reason to install it (PRELUDE then PAYOFF then a trailing blank-line
ASIDE, `git am` reconstitutes the tree), v0.2 was forced by `git log`
after am, not polish. Do not collapse into `git format-patch`. Do not
grow a compiler in v0.
