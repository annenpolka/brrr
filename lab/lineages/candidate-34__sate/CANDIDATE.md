# candidate-34 — sate

## Primitive

A unified diff is a set of before→after image claims; `sate` reports how a tree occupies each claim (APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED), not whether `git apply --check` is a boolean.

## Four primitives considered

1. **sate** — patch occupancy against a tree; `sate --log` asks which historical patches still occupy HEAD; `--suggest` treats review `suggestion` fences as one-hunk patches. **Implemented.**
2. **assay** — expected values in tests (`assertEqual` second args, snapshots, goldens) as a time series: RATCHET / FLIPFLOP / WEAKEN. Not implemented; suggested mutation.
3. **taken** — a standalone tool whose only object is GitHub ` ```suggestion ` blocks. **Discarded:** it is sate with a different parser, not a second primitive.
4. **chide** — a review comment's quoted snippet as a still-true predicate. **Discarded:** `slip` + grep; leftover-claim adjacent to zanei.

`assay` is real (snapshot tests that bounce; timeouts that only ever increase) but it is a dashboard over literals. Occupancy is a verb `git apply --check` has been lying about for twenty years.

## Why this might not exist

`git apply --check` and `git apply --reverse --check` are the folk pair for "would apply" / "already applied". They are booleans per patch, they fail when *context* drifted even though the change-core is in the tree, and they cannot say MIXED (partial apply) or DUPLEX (both images live, as a copy). GitHub's "outdated" review comment is line-identity, which is the same lie on a different object.

The occupancy sandwich is the correctness property: `sate --git C --against C` is APPLIED; `--against C^` is PENDING. A review suggestion is the same sandwich at hunk grain.

## How to run

From the worktree root:

```bash
./sate --help
./sate --selftest
./sate --selftest --fuzz
./demo.sh
./sate --git HEAD
./sate --log 8 -C /path/to/repo
./sate --suggest fixtures/suggest.jsonl -C fixtures-tree
```

Exit: `0` unanimous APPLIED (or empty), `1` unanimous PENDING, `2` SPLIT / MIXED / DUPLEX / SUPERSEDED, `3` error. `--report-only` forces `0`. `--json` / `--tsv` compose.

## Empirical transcript

### v1 (exact blocks + change-core + subsequence; fuzz off)

`./sate --selftest --no-fuzz` → 21 then 22 passed (parser + sandwich). Fixture demo: APPLIED / PENDING / SUPERSEDED / MIXED all matched; exit codes 1 and 2 matched.

**False DUPLEX on addition hunks.** `@@ -225,6 +235,35 @@` is 6 context lines plus an inserted body. The before-image *is* a prefix of the after-image, so `find_all(before)` and `find_all(after)` both hit the same locus. Dogfood:

| repo | `sate --git HEAD --against HEAD` |
| --- | --- |
| kizu | APPLIED |
| sitbone | APPLIED |
| relico | APPLIED |
| voidtrace | **SPLIT APPLIED=224 DUPLEX=21** |
| tenaoshi | **SPLIT APPLIED=12 DUPLEX=3** |

All 21 voidtrace DUPLEX hunks were pure additions (`scenario-domain.test.ts`, `execution.ts`, …). Same for tenaoshi's `OraclesGenerated.swift` / `tenaoshi.pkl`. The sandwich was right about the after-image and lying about leftover before.

`--log` with `--first-parent --no-merges` on kizu printed 6 version-bump commits: GitHub mainline is merges. The interesting patches live off first-parent.

### v2 (one improvement, two dogfood findings)

1. **Prefix rule.** Pure addition: after-image present ⇒ APPLIED, even if context (the before-image) is a prefix of after. Pure deletion is the mirror. Modify hunks with *independent* leftover copies stay DUPLEX. Shared-context fuzz MIXED (0.50/0.50 on `def add`) was also gated on unique `+`/`-` cores.
2. **`--log` topology.** Default is `--no-merges` without `--first-parent`. `--first-parent` remains for merge-mainline walks.

After v2: voidtrace and tenaoshi sandwiches are unanimous APPLIED / PENDING. `./demo.sh` **31 passed, 0 failed**.

kizu `--log 8` after the topology fix:

```
APPLIED       2h  9349dc50  release: v0.7.0
APPLIED      74h  04adde1f  feat: add complete jsx tsx support
SPLIT         2h  88362116  release: v0.6.0     PENDING=1 SUPERSEDED=1
APPLIED       8h  c0d963ff  perf: speed up stream file rebuilds
SPLIT        44h  54cdccfc  perf: add operation benchmarks …  APPLIED=43 SUPERSEDED=1
APPLIED       1h  4a13f886  fix: gate macos-only init re-export
APPLIED      11h  bbdc37d7  refactor: split watcher responsibilities
SPLIT        11h  f9fba257  refactor: split hook responsibilities  APPLIED=7 SUPERSEDED=4
```

v0.6.0 vs HEAD: `Cargo.toml` SUPERSEDED (now 0.7.0), one `Cargo.lock` hunk still PENDING (core-minus still in the lockfile). That is occupancy, not `git log -S`.

sitbone `--log 10`: 8/10 fully APPLIED; two older commits each have a single SUPERSEDED hunk. A history that still occupies itself.

voidtrace `--log 8`: HEAD feature 245 hunks APPLIED; the previous two features (`c8f7400`, `90fd2e5`) are SPLIT with ~100 SUPERSEDED and some PENDING. PENDING occupancy of an ancestor means HEAD restored that hunk's *preimage* — a revert without a revert commit.

## Dogfood targets

- `sate --selftest` / `--selftest --fuzz` (24 each): exact fates, create/delete, context-drift core, sandwich git repo, Japanese path with spaces, suggestion JSONL + GitHub body extract, addition-prefix not DUPLEX.
- `./demo.sh` fixtures: four fates, stdin, suggest TAKEN/OPEN/gone, log of a version-ratchet history.
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,voidtrace,tenaoshi,relico}` sandwich + `--log`.

## Surprises

- The occupancy sandwich held on the first try for kizu/sitbone/relico. The failures were all *addition hunks*, which is the common case in feature commits.
- GitHub-style repos make `--first-parent --no-merges` look at version bumps and miss the work.
- DUPLEX on a sandwich is usually a parser accident (context ⊆ after), not copied code. True duplex needed a fixture that literally contained both function bodies.
- `sate --suggest` on a three-line JSONL classified TAKEN / OPEN / gone in one pass — review comments did not need a second tool.

## Failures

- Binary patches are SKIP/BINARY, not occupied.
- Combined merge diffs are not parsed; `--log` skips merges.
- Generic change lines (`}`, `else:`) are filtered from subsequence matching; a hunk that *only* moves braces falls through to SUPERSEDED more often than a human would.
- `--fuzz` is still opt-in. Default stays the exact/core/subseq cascade after the prefix fix.

## Suggested mutations

- **assay** — oracle expected-values as a time series (the discarded-but-kept idea).
- `sate log --pick SUPERSEDED` — emit the hunks that left HEAD, as a patch.
- GitHub review API ingest (`gh api repos/…/pulls/…/comments`) without a file.
- `--against :` (index) and a `sate watch` that re-classifies a patch as you edit.
- Treat MIXED as a split of the hunk: which `+`/`-` lines landed.

## Kill / keep

**Keep.** The object is small (a hunk's two images), the verb is missing (`git apply --check` is a boolean lie), review suggestions are the same object, and the sandwich is an empirical invariant that survived five real repositories after one matcher fix.
