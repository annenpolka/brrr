# hybrid-17 — kit

## Primitive

`--code` grain: copy+edit occupancy ignores dest boilerplate imports/headers so the covering names the extract, not `use anyhow::Result`. Still COPY vs FOLLOW.

## Why this might not exist

crib occupies dest as a new holder of a blob. ditto covering can spend a sheaf slot on leftover dest *boilerplate* (`grep -F 'use anyhow::Result;' -- src/init/install.rs`) instead of the extract. Dest *name* leftover is already dead (`grep install.rs`); dest *boilerplate* is not.

The recurring annoyance: you extracted `src/init.rs` into `src/init/install.rs`, occupancy tools correctly say COPY (source still holds), then the extra copy+edit slot asks you about `use anyhow::Result` — a line that only "splits" because dest is new. Shared anyhow also false-pairs two unrelated extracts at Jaccard 0.55.

Discarded as too conventional: wrapping `git diff -C`, leftover-name search as the product, a third occupancy ambit, stuffing `--code` onto ditto as a silent filter without naming the extract.

## How to run

```bash
./kit --help
./demo.sh 0
./kit -C /path/to/repo HEAD~1 HEAD
./kit -C /path/to/repo --limit 6 5671a72^ 5671a72
./kit --no-code -C /path/to/repo --limit 6 5671a72^ 5671a72
./kit -C /path/to/repo --held 14b1d6e^ 14b1d6e
./kit HEAD :worktree
```

Python 3.9+, stdlib only, `git`. Exit 0 iff a sheaf was found.

## Empirical transcript

### Before the improvement

v1 strips dest import/header lines from Jaccard and from covering content, then emits a path-scoped grep of an extracted definition. `--no-code` recovers ditto.

**Exact `cp a.rs b.rs` (both exist):** copy, walks `exists b.rs` without `--follow`.

**kizu C056** `--code` names the extract, not anyhow:

```
$ ./kit -C kizu --limit 6 5671a72^ 5671a72
# C   26  copy src/init.rs → src/init/install.rs
# B   45  grep kizu_hook_command -- src/init/install.rs
# B   18  grep -F 'の巨大ファイルを'
# A   27  grep PathBuf -- src/init.rs
# not use anyhow::Result
# not exists *install*
# not follow
```

**kizu C056 `--no-code`** still steals the slot:

```
# C   copy src/init.rs → src/init/install.rs
# B   grep -F 'use anyhow::Result;' -- src/init/install.rs
```

**Shared anyhow, different extracts:** `--code` copies=0 (dest is a birth). `--no-code` copies=1 at Jaccard 0.556 (`a.rs` → `b.rs`).

**kizu R100** still one follow. **sitbone** FocusRiverView stays `grep FocusRiverView`.

Failure: dest spends *two* slots (copy + shortest shared helper `kizu_hook_command`). The edited extract surface is `kizu_bin_for_scope` / `install_agent` (dest-only `pub(super)` wrappers). Shortest-of-shared named a copied helper.

### After the improvement

Forced by that kizu transcript, not polish. Prefer dest-only definition names (the edited extract surface, dest file order) over the shortest verbatim-copied helper.

```
$ ./kit -C kizu --limit 6 5671a72^ 5671a72
# C   26  copy src/init.rs → src/init/install.rs
# B   46  grep kizu_bin_for_scope -- src/init/install.rs
# B   18  grep -F 'の巨大ファイルを'
# A   27  grep PathBuf -- src/init.rs
# not kizu_hook_command (verbatim helper)
# not use anyhow::Result
```

`--no-code` still steals with anyhow. Sitbone / R100 unchanged.

`./demo.sh 0` — 35 assertions. Exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — C056 `src/init.rs → src/init/install.rs` dest boilerplate vs R100 follow
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView birth/death/island; cover stays `grep FocusRiverView`
- synthetic: extract-and-edit with dest anyhow header; unrelated extracts sharing anyhow; `cp` vs `git mv`; remaining-blob twin; directory copy; spaces rename; nested git; `:worktree`; empty repo

## Surprises

- Exclusive-side same-SHA is still not enough to decide follow. Remaining holder is copy.
- dest-on-B vs source-on-A Jaccard *rises* after stripping dest-only rewritten imports (kizu 0.551 → 0.565). Shared anyhow was hurting the extract number; dest-only `use super::` was hurting it more.
- Shared anyhow is enough to *false-pair* two unrelated extracts (Jaccard 0.556) when `--no-code`. --code grain is copy detection, not only covering.
- Tree-wide grep of an extracted fn is TRUE on A (source) and B (dest). Path-scoped to dest names the occupant of the new holder. That is dest occupancy restated, but it names the extract.
- Dest *name* leftover (`grep install.rs`) was already dead. Dest *boilerplate* was the remaining thief.

## Failures

- v1 shortest-of-shared named `kizu_hook_command` (verbatim helper) instead of dest-only `kizu_bin_for_scope`. v2 dest-only file order.
- Copy dest still occupies two sheaf slots (copy + extract). Other changed files (pre_commit.rs) go unexplained under `--limit 6`.
- Similarity copies can still glue coincidentally similar new files that share a body, not just a header. `--no-copy` recovers.
- Generated `held --follow exists` is still pasteable; current `held` (candidate-09) does not parse `--follow`. Copy walks are `exists DEST` and run today.

## Suggested mutations

- Fold the extract name onto the copy glyph so dest does not spend a second slot.
- `kit A B | crib` occupancy-in, eras-out, without `sh`.
- Query-restricted similarity at fat merges (crib's first-parent miss).

## Flipped assumption: bought and lost

Parent ditto assumed **copy+edit still wants a unary glyph of dest, and unique dest lines are the glyph**. Parent crib assumed **line Jaccard of dest-on-B vs source-on-A is the extract number**.

**Bought**

- Dest boilerplate is not a covering question. The extract definition is.
- Shared anyhow is not a copy. Unrelated extracts that share a header stay births.
- `git mv` remains FOLLOW. Exact `cp` remains COPY. Sitbone unique birth stays `grep FocusRiverView`.
- `--no-code` is an explicit downcast, not a fork.

**Lost**

- Unique dest lines are no longer automatically covering: `use anyhow::Result` unique-to-dest-path is dest birth restated.
- Raw line Jaccard is no longer the extract number when the overlap is imports.

## Kill / keep

**Keep.** It is not ditto with a skip-list and it is not `git diff -C`. On the first real recorded copy (`C056`, blob still at `src/init.rs`) `--code` named `copy src/init.rs → src/init/install.rs` plus an extract grep, and `--no-code` still printed `use anyhow::Result`. Shared anyhow false-pairs; `--code` refuses. Sitbone stayed `grep FocusRiverView`. Copy vs follow is still empirically distinct. Boilerplate no longer steals the copy+edit slot.
