# candidate-24 — alibi

## Primitive

Transplant the *current* test suite onto *another revision's production files*; tests that fail are the production diff's alibi.

## Four primitives considered

1. **alibi** — splice current tests onto base production; LOCKED vs LOOSE. **Implemented.**
2. **flotsam** — unique bytes on disk for this repo that are not in HEAD (stash, other worktrees, vim swap, dangling blobs). Recover-lost-work.
3. **took** — critical-path wait chain of a live process tree. Discarded: conventional-adjacent to `time`/`hyperfine`/`offcputime`.
4. **bleed** — filesystem/port crosstalk from one test into another. Discarded: conventional-adjacent to `pytest-randomly` / isolation runners.

`took` and `bleed` are real annoyances with existing verbs. `flotsam` is interesting (named gap: recover-lost-work) but is a search, not a new interaction with running tests. `alibi` is the missing CI check TDD assumes: **the new tests must go red on the old production tree.** Coverage and "run tests on the parent commit" both get this wrong — the latter runs *old* tests on old code; `alibi` keeps *new* tests.

## Why this might not exist

CI runs tests on HEAD of the PR. Nobody routinely checks that those tests *fail without the production hunks*. You can merge tests that already passed on main, or production edits whose tests never asserted the new behavior. Mutation testing randomly perturbs AST operators; `alibi` perturbs *your actual diff*, and only the production side of it.

Diff-coverage says a line executed. Execution is not a veto.

## How to run

From the worktree root:

```bash
./demo.sh
./alibi --help
./alibi HEAD --list
python3 -m unittest discover -s tests -v
```

## Empirical transcript

### v1 (`fa08ea3`) — 22 tests, fixture demo PASS

`./demo.sh` exit 0. LOCKED / LOOSE / CLEAN / BROKEN all matched.

`--list` on kizu (dirty worktree): **1 production path: `AGENTS.md`**. A symlink to `CLAUDE.md`. Tests would have been asked to "lock" a doc edit.

Self `--list` while still mixed with the lab tree was noise. After orphaning `candidate-24`, a clean self-run hit a real bug:

```
./alibi HEAD --cmd 'python3 -m unittest discover -q'
status=BROKEN  NEW fail(5)  0.03s
Ran 0 tests in 0.000s
NO TESTS RAN
```

Python 3.14 `unittest discover` from `.` does not recurse into `tests/` unless it is a package. Fixtures worked only because `test_adder.py` sat at the repo root. The tool could not dogfood itself.

voidtrace `--list` treated `data/fixtures/golden/*.json` as production (would overlay/delete them in a splice). tenaoshi reported **89** "production" paths, including `AGENTS.md`.

### v2 — file roles + `-s tests` + skip empty diffs + `--per-path`

After the improvement:

- Self vs `fa08ea3` (uncommitted v2): **LOCKED**. Witnesses were exactly the new tests (`test_fixtures_are_tests`, `test_markdown_only_is_clean`, `test_detect_unittest_default`, …).
- Self `--per-path`: **`alibi.py` LOCKED, `demo.sh` LOOSE**. The demo script changed but no test vetoes it. That is the mixed-diff case v1 could not see.
- kizu: dirty `AGENTS.md` → **CLEAN**, cargo never launched (`skipped test runs`).
- sitbone: 0 production source diffs.
- tenaoshi: 89 → **28** Swift/source paths (docs dropped).
- voidtrace: golden JSON dropped; **8** `.ts` production paths remain.

`./demo.sh` still exit 0, now including a mixed `--per-path` fixture.

Post-commit (`f433c1d`): `./alibi HEAD` → **CLEAN** (skipped tests). A comment inserted into `alibi.py` → **LOOSE** (NEW pass, SPLICE pass, exit 2). Then `git checkout -- alibi.py`. `./demo.sh` still 0.

## Dogfood targets

- `tests/test_alibi.py` fixtures (LOCKED, LOOSE, CLEAN, BROKEN, added module, tests/, markdown-only, mixed per-path).
- This repo vs `HEAD` (v2 tests as witnesses for v2 `alibi.py`).
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,tenaoshi,voidtrace}` `--list`; kizu full run.

## Surprises

- Coverage-adjacent tools would have called kizu's `AGENTS.md` a "changed file." alibi's object is *production source*. Once docs were excluded, kizu was honestly CLEAN.
- `--per-path` on this repo split a two-file dirty tree into LOCKED tool code and LOOSE demo script without being asked which file mattered.
- unittest 3.14 silent `NO TESTS RAN` / exit 5 looked like a red suite. BROKEN now prints the new-tree tail.

## Failures

- v1 could not self-host under Python 3.14 default discover.
- `demo.sh` is a `.sh` file, so it counts as production. Tests do not lock it (LOOSE). Fine, but a `--not-production` glob would be nicer than hoping the heuristic agrees.
- Did not run `cargo test` / `swift test` / `vitest` splices on kizu/sitbone/voidtrace: kizu and sitbone had no source diff; tenaoshi/voidtrace have large dirty source trees and full-suite splice would be minutes × N paths.

## Suggested mutations

- Per-hunk overlay, not just per-path.
- Reuse coverage to pick a test subset before the splice run.
- Treat `UNBUILDABLE` ImportError of a *new* module as LOCKED-by-existence.
- Stream JSONL of per-path results as they complete.
- `--src GLOB` / `--ignore GLOB` to override the source-extension heuristic (demo.sh, justfile).

## Kill / keep

**Keep.** The splice is a different object than delta-debugging a dirty tree: tests stay at *new*, production at *base*. Dogfood produced a LOOSE path (`demo.sh`) a human agrees is untested and LOCKED witnesses that are real assertions. Not `git stash -k && test` — stash would revert the new tests too.
