# candidate-39 — canto

## Primitive

A mixed commit has a **plot**: name-closed acts in required reading order.
A name is a plot point if this diff defines it (natal, touched, or enclosing
type). An act is a strongly-connected, name-closed set of hunks. Later acts
may use earlier defs; the reverse is TANGLE. Independent name sets are tracks.

Not leftover names. Not inverse-printf. Not occupancy. Not path-conditions.

## Four primitives considered

1. **canto** — narrative-split of a commit by name-closed acts (PRELUDE /
   PAYOFF / ASIDE / SPOIL / CYCLE). **Implemented.**
2. **muster** — test *identity* as a time series (BORN / RENAME / SPLIT /
   MUTE / THIN / RETARGET / VANISH). **Discarded:** tide already walks tests
   as oracles; RETARGET (gaze moved, expected value stable) is a real object
   but is a mutation of tide, not a first tool. Parked.
3. **slack** — assertion-*strength* career (`assertEqual` → `assertIn` →
   `assertTrue` = WEAKEN). **Discarded:** tide for predicates.
4. **cadence** — per production name, LEAD / LOCKSTEP / LAG / BARE of the
   tests that cite it, over history. **Discarded:** alibi/cinch-adjacent
   without a new object; would be a history-walk mutation of canto's spoil.

`scene` (orbit) and `tale` (due) parked this verb as “git add -p with
clustering unless there is a compile-oracle.” The oracle here is **def→use
closure on this diff's own plot names**, not a compiler and not file
clustering. Two features with disjoint natal names are two tracks even
inside one commit.

## Why this might not exist

Reviewers of a 14-file squash reconstruct the story by hand: types, then
impl, then tests, then the README. `git add -p` asks you to choose hunks.
`git-absorb` / stacked-PR tools need you to already know the layers.
Coverage says a line ran. alibi says the *tree* is locked. Nobody emits
the **required reading order** of the blob you just dumped.

The cheat canto names is silent: tests and production of a new type land
in one SCC (**SPOIL**), or a lockfile/docs ride along and pretend to be
the payoff. `--check` is the CI form.

## How to run

From the worktree root:

```bash
./demo.sh 0
./canto --selftest
./canto --help
./canto -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone e9b0f75
./canto -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --grain file --check 04adde1
./canto -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --grain file edf2de9
git diff A B | ./canto --stdin --format tsv
```

Python 3.9+, stdlib, `git`. `./canto` is the CLI.

## Empirical transcript

### v0.1 — every context def is a plot point, including fields

`./canto --selftest` 26/26. Fixture mixed Python: Lexer → Parser → tests,
util on its own track, README ASIDE. Two-feature rust fixture: Alpha and
Beta tracks. Touched Swift class before its tests.

Real repos:

- **sitbone `e9b0f75`** (dual-threshold hysteresis) — the money shot
  *almost*: PresenceArbiter.swift was **five PRELUDE acts** (one per hunk),
  then PresenceHysteresisTests PAYOFF via PresenceArbiter. The blank-line
  edit to PresenceArbiterTests.swift was **SOLO** (context `struct` counted
  as a def), not ASIDE.
- **kizu `04adde1`** (jsx/tsx feature dump) — one giant track, Cargo.lock
  and README were **PAYOFF** via `source` / `tree` / `tsx`. File order led
  with `file_view.rs` because field name `content` was a fake prelude.
- **kizu `edf2de9`** (split git types) — types.rs / revert.rs readable, but
  `PathBuf` / `status` were vias. plans.md was PAYOFF of `repo`.

### v0.2 — after dogfood (one improvement)

Plot points are **natal ∪ touched ∪ enclosing types**. Context-only
function defs and `name: Type` fields are not plot points. doc/config
paths do not enter the graph (they are ASIDE). Adjacent same-file SCCs
merge into one act. Whitespace-only hunks are ASIDE.

After:

- sitbone `e9b0f75` file *and* hunk grain: **3 acts, 2 tracks**.
  `#1 PRELUDE PresenceArbiter.swift` (presentThreshold, absentThreshold,
  applyHysteresis) → `#3 PAYOFF PresenceHysteresisTests.swift` via
  PresenceArbiter. `#2 ASIDE` the blank-line sibling test file.
  `--check` exits 0.
- kizu `04adde1`: Cargo.lock, README, SPEC, ADR, plans are **ASIDE**.
  `--check` exits **1** because `src/highlight.rs` (+ in-file `#[test]`)
  and `src/hook/tests.rs` are SPOIL. That is the right CI signal for a
  feature dump, not a false lockfile payoff.
- kizu `edf2de9`: `types.rs` (#3) before `revert.rs` (#4, via LineKind,
  Hunk). plans ASIDE. repo.rs is a separate SOLO track (no name edge from
  `mod repo` — honest: the module name is not a type use).
- tenaoshi `4878b75`: oracle-value tweak, mostly ASIDE. Narrative-empty is
  a result (tide's object, not canto's).
- Fixture squash `--against` three story commits: **mean_jaccard=1.0**.
  `--split --verify` reconstitutes TO.

`./demo.sh 0` exit 0 (27 selftests, 14 unittests, 15 demo asserts).

## Dogfood targets

- Synthetic fixture in `demo.sh` (Lexer/Parser/tests + util track + README
  aside; squash recovery; split-verify; spoil --check).
- `tests/test_canto.py`.
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi}`.

## Surprises

- File clustering would have put PresenceArbiter.swift + both test files
  in one “tests+prod” pile. Name-closure puts only the test that *uses*
  PresenceArbiter in PAYOFF; the blank-line sibling is ASIDE.
- `--against` on *already well-split* kizu commits (`edf2de9^..3b3e0a9`)
  scores 0.21 — the recovered order is type-flow, not author-commit
  boundaries. The fixture (Lexer then Parser then tests) scores 1.0.
  against measures “was this squash a story?”, not “did we invert git log.”
- Rust `#[test]` in the same file as prod is SPOIL at file grain and a
  later PAYOFF at hunk grain. `--grain` is the object, not a format flag.
- kizu `mod js_ts` is a prelude; `tests/e2e/jsx-tsx.test.ts` did **not**
  cite `JsTsDialect` so it sits as its own PRELUDE (`scarred`, `session`)
  instead of PAYOFF. Gaze that lives only in strings is invisible.

## Failures

- `git.rs` PAYOFF of `read_file_at_revision` after the e2e test prelude is
  backwards-looking: a re-export hunk ranked late. Topo is correct given
  the edges; the edges miss “this file is the module root.”
- Common short natal names (`last`, `out`, `rel`, `old`) still mint defs.
- No compile-oracle: a name-closed act can still fail to typecheck (Python
  `ast.parse` of prefixes is a suggested mutation).
- `--split` is file grain. In-file prod+test (Rust `mod tests`) cannot be
  unsquashed into two commits without a formatter.
- Binary / generated files skipped; lockfiles are ASIDE, not “the dep that
  the prelude needs.”

## Suggested mutations

- **muster** — the discarded test-identity time series; RETARGET is the
  payload tide cannot see.
- **canto --tdd** — PAYOFF first (red), then PRELUDE (green): chronological
  TDD rather than reading order.
- **ast.parse / rustc --parse** as a true compile-oracle on act prefixes.
- Module-root files (`mod foo`, `__init__.py`) count as definers of `foo`.
- `canto given` — fail CI if a PR range is a single SPOIL act.

## Kill / keep

**Keep.** The object is the **act**, sitbone `e9b0f75` is a one-screen
reason to install it, v0.2 was forced by kizu lockfile-as-PAYOFF and five
prelude hunks, not polish. Do not collapse into `git add -p`. Do not grow
a compiler in v0.
