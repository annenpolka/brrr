# candidate-32 — veil

## Primitive

A production diff's **cover-type** against the test suite: each changed name is LIVE (uncited mock, real call), VEIL (tests only see a mock of it), or BARE (nobody cites it).

## Four primitives considered

1. **veil** — mock-vs-diff cover-type. **Implemented.**
2. **pith** — assertion catalog of tests joined to identifiers in a production diff, no mock object. Useful, but without VEIL it is grep with extra steps. Absorbed as the LIVE/BARE axes.
3. **waive** — deleted test assertion pins whose production still lives. Discarded: judges will collapse it into leftover-names / inverse-zanei.
4. **braid** — pairwise splice of production files; independently green, jointly red. Discarded: adjacent to `alibi --per-path` and hybrid `cinch`.

## Why this might not exist

Reviewers see a new test file and a green suite and believe the production change is locked. Coverage agrees if the mock executed. `alibi` agrees if the *tree* is necessary for the suite to stay green — a mock of `checkout` still fails when `checkout` is deleted, so the tree looks LOCKED. Nothing asks the static question: **is the test looking at the new body, or at a fake?**

The missing Unix verb is a join of `(changed production names) ⋈ (test mocks ∪ test citations)`.

Not leftover names, not inverse-printf, not wait-for, not spec-gen freshness.

## How to run

```bash
./veil --help
./veil --self-test
./demo.sh
./veil --from HEAD~1 --to HEAD --explain
./veil -C /path/to/repo --from origin/main --to HEAD --json
./veil --check
```

Python 3.10+, git, stdlib only. Exit 0 on analysis success. `--check` exits 1 if status is THEATER, EXPOSED, or OPEN. Errors exit 2.

## Empirical transcript

### v0.1 (this commit)

`./demo.sh` and `./veil --self-test` both exit 0. Ugly fixture:

```
status=OPEN  names=8  LIVE=2  VEIL=3  BARE=3
LIVE   add               shop.py                 (tests/test add.py — space in path)
VEIL   checkout          shop.py                 mock shop.checkout
BARE   retry_budget      shop.py
VEIL   loadTemplate      src/loader.ts           vi.mock('./loader.js')
LIVE   compose           src/composer.ts
```

Dogfood, 2026-08-20, read-only `-C` (originals not mutated):

| repo | range | status | LIVE | VEIL | BARE | note |
| --- | --- | --- | --- | --- | --- | --- |
| soul-writer | HEAD~3 | OPEN | 16 | 7 | 25 | VEIL is real: `provider-factory.test.ts` `vi.mock('./cerebras.js')` hides `formatLastError` / `getRetryAfterMs` / `makeStrictSchema` |
| voidtrace | HEAD~1 | EXPOSED | 11 | 0 | 37 | internals in `evaluate.ts` (`function createPhaseEvents`, not `export`) flood BARE |
| kizu | HEAD~1 | CLEAN | 0 | 0 | 0 | release commit, no production |
| kizu | HEAD~5 | EXPOSED | 20 | 0 | 582 | ui.rs split: every fn in new files counts as changed |
| sitbone | HEAD~1 | EXPOSED | 0 | 0 | 7 | Swift views in NotchOverlay; no XCTest cites the new names |
| skills | HEAD~1 | CLEAN | 0 | 0 | 0 | docs-only |
| tenaoshi | HEAD~1 | EXPOSED | 0 | 0 | 13 | **bug:** `Engine/Tests/.../OraclesGenerated.swift` treated as production (`Tests` ≠ `tests`) |

### After the first improvement (v0.2)

Fixes from the v0.1 dogfood, not from taste:

1. `Tests/` and `TenaoshiEngineTests` are test paths (case-insensitive; `*Tests` segments).
2. Brace-accurate def spans, so an edit to `touch()` does not mark neighboring `keep()` as changed. v0.1's 4000-char window was a firehose.
3. Unexported **BARE** helpers are hidden by default (`--all-names` restores them). Unexported **VEIL** still prints — that is the theater.
4. Duplicate porcelain rows from walking a `@patch` decorator twice.

Re-run on the same ranges:

| repo | range | v0.1 | v0.2 |
| --- | --- | --- | --- |
| soul-writer | HEAD~3 | OPEN 16/7/25 | **EXPOSED 13/0/4** |
| voidtrace | HEAD~1 | EXPOSED 11/0/37 | **COVERED 5/0/0** |
| kizu | HEAD~5 | EXPOSED 20/0/582 | EXPOSED 19/0/233 |
| sitbone | HEAD~1 | EXPOSED 0/0/7 | EXPOSED 0/0/4 (`EndSessionButton` still BARE) |
| tenaoshi | HEAD~1 | EXPOSED 0/0/13 (oracles as prod) | **CLEAN** |
| this repo | vs v0.1 | — | EXPOSED 8 LIVE / 8 BARE on `veil.py` (tests cite `analyze`, not `classify_name`) |

Surprise: soul-writer's seven VEILs were **false**. `formatLastError` / `getRetryAfterMs` did not change; v0.1 hashed a window that overlapped the edited `CerebrasClient`. After brace spans they vanish, and `CerebrasClient` is LIVE via `cerebras.test.ts`. The ugly fixture still reports VEIL on `checkout` and `loadTemplate` — the object is real, the first dogfood hit was a span bug.

voidtrace `evaluate.ts` internals (`createPhaseEvents`, …) were unexported BARE. Public `evaluateScenario` / `executeForcedSlashDurationRule` are LIVE. Status COVERED: the production diff's *public* names are cited.

sitbone still names the finding a reviewer wants: new SwiftUI views with no XCTest citation.

Self `--self-test` and `./demo.sh` still exit 0 (13 unit tests).

## Dogfood targets

- Synthetic ugly fixture (`--self-test`, spaces, `実験/`, nested git, JS + Python mocks)
- `/Users/annenpolka/ghq/github.com/annenpolka/{soul-writer,voidtrace,kizu,sitbone,skills,tenaoshi}`
- This repo vs HEAD after the tool exists

## Surprises

- soul-writer's VEILs were not false positives. The factory test mocks the collaborator *modules*, so helper changes inside `cerebras.ts` / `codex-client.ts` have no live test. `CerebrasClient` itself is LIVE (cited by name). Cover-type is per-name, not per-file — that split is the primitive.
- `alibi` would call a mocked SUT LOCKED (delete the function, the mock setup still needs the module). veil is the tool that says THEATER instead.
- kizu HEAD~1 is honestly CLEAN; HEAD~5 is a file-split firehose. The primitive is not occupancy.

## Failures

- v0.1: `Tests/` (Swift) treated as production. Fixed.
- v0.1: overlapping def windows invented VEIL/BARE. Fixed for braces; Python already used AST dumps.
- kizu HEAD~5 is still a file-split firehose (233 pub names born in new files). Cover-type is not occupancy; `akin`/`once` own that.
- Short JS `vi.mock('node:fs/promises')` is ignored (external). Correct, but a test that *only* mocks node builtins never veils a SUT — SCRIPT status is a mutation.
- Python `import shop` must not LIVE every name in `shop.py` — citation of the *name* is required. (Caught in self-test design, not dogfood.)

## Suggested mutations

- `--same-module` / SCRIPT status: collaborator mocks (test SUT is a different file) vs SUT veils
- Assertion-literal join (`pith`): expected values in tests ∩ literals in the production diff
- Gitless stdin patch: `git diff \| ./veil --diff -`
- Swift `XCTest` / Rust `#[test]` as first-class test spans, not whole-file idents

## Kill / keep

**Keep.** The object is new: not leftover names, not a test run, not coverage. soul-writer produced a real VEIL on the first real JS repo. The first improvement is about *which names are the review object*, not about whether cover-type is the right question.
