# kit

Shortest covering set of predicates that distinguish two git trees, as ready-to-run `held` / `berth` lines — **copy vs follow**, with a **`--code` grain**.

`tell` lists unary questions. `sheaf` prints a covering set plus walks. `ditto` distinguishes copy from follow, then spends a sheaf slot on leftover dest *boilerplate* (`use anyhow::Result`) for copy+edit. `crib` occupies dest as a new holder of the blob.

`--code` grain: copy+edit occupancy ignores dest boilerplate imports/headers so the covering **names the extract**, not `use anyhow::Result`. Dest *name* leftover (`grep install.rs`) stays dead. Still COPY vs FOLLOW.

Not `git diff --name-status -C`. Not glyph. Not leftover-name search. Not a third occupancy ambit.

kit itself does not walk history. Default stdout is the sheaf (comment-prefixed covering set) plus pasteable occupancy commands. `kit A B | sh` may run `held`. `--held` / `--berth` pick the walker. `--no-code` recovers ditto's raw-line covering.

## Install / run

```bash
# from this directory
./kit --help
./demo.sh 0
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `kit` onto your `PATH` if you want. Generated walk lines assume `held` and `berth` are on `PATH`. Copy walks are `exists DEST` (no `--follow`: the source still holds). Follow walks are `--follow exists OLD`. Extract walks are `grep EXTRACT -- DEST`.

Exit codes: `0` a sheaf was found, `1` the trees are identical (or nothing distinguished them), `2` tool error.

Refs may be any tree-ish: `HEAD~1`, a sha, a tag, `:worktree`, `:index`.

## Examples

**1. Copy+edit names the extract, not dest boilerplate.**

```bash
kit -C kizu --limit 6 5671a72^ 5671a72
kit --no-code -C kizu --limit 6 5671a72^ 5671a72
```

```
# kit 69dea6f..5671a72  (kizu, code)
# C   26  copy src/init.rs → src/init/install.rs
# B   46  grep kizu_bin_for_scope -- src/init/install.rs
held -C kizu --rev 5671a72 --limit 12 exists src/init/install.rs
held -C kizu --rev 5671a72 --limit 12 grep kizu_bin_for_scope -- src/init/install.rs
```

`--no-code` recovers `grep -F 'use anyhow::Result;' -- src/init/install.rs`. Dest *name* leftover (`exists *install*`, `grep install.rs`) stays dead either way.

**2. `cp a.rs b.rs` is copy. `git mv a.rs b.rs` is follow.**

```bash
kit A B                 # default --copy --follow --code
kit --no-copy A B       # dest is a birth (exists)
kit --no-follow A B     # rename is two exists
kit --no-code A B       # dest boilerplate may steal a slot
```

```
# C   11  copy a.rs → b.rs                                  1 path
held -C repo --rev B --limit 12 exists b.rs

# R   32  follow 'old name.txt' → 'new name.txt'            2 paths
held -C repo --follow --rev B --limit 12 exists 'old name.txt'
```

Same blob still on A and also born on B is **copy**, not follow. Shared `use anyhow::Result` is not enough to pair two unrelated extracts.

**3. A unique birth stays `grep FocusRiverView`. An island vs HEAD still prints `--full`.**

```bash
kit -C sitbone 14b1d6e^ 14b1d6e
kit --berth --walks -C sitbone 14b1d6e HEAD
```

FocusRiverView is not a crib dest and not a copy. Cover stays the name, not leftover CJK.

## Flags that matter

| flag | meaning |
| --- | --- |
| `--code` | ignore dest boilerplate imports/headers; copy+edit names the extract (**default**) |
| `--no-code` | raw lines: dest boilerplate may steal a copy+edit slot (ditto mode) |
| `--held` / `--berth` | pick the walker (default: held, so `kit A B \| sh` runs occupancy) |
| `--walks` / `--sh` | only command lines |
| `--copy` | same blob still on A and born on B is copy (**default**) |
| `--no-copy` | dest is a birth (`exists dest`) |
| `--follow` | rename is one identity (**default**) |
| `--no-follow` | path existence is identity (two exists) |
| `--full-walks` | force `--full` on every walk |
| `--no-walks` | sheaf only (still comment-prefixed) |
| `--predicates` | also print tell's ranked catalog |
| `--limit N` | max size of the sheaf |
| `--json` | `sheaf`, `walks`, `identities`, `unexplained`, `code` |
