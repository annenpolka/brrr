# ditto

Shortest covering set of predicates that distinguish two git trees, as ready-to-run `held` / `berth` lines — **copy vs follow**.

`tell` lists unary questions. `sheaf` prints a covering set plus walks. `glyph --follow` treats a same-blob path change as one identity. That is correct for `git mv`. It is wrong when the blob remains on A.

ditto emits **copy** (both names exist; B is a new holder of the same blob) vs **follow** (A name gone; B name is the same identity). Path existence is not identity.

ditto itself does not walk history. Default stdout is the sheaf (comment-prefixed covering set) plus pasteable occupancy commands. `ditto A B | sh` may run `held`. `--held` / `--berth` pick the walker.

Not `git diff --name-status -C`. Diff lists letters. ditto names the questions you paste into occupancy.

## Install / run

```bash
# from this directory
./ditto --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `ditto` onto your `PATH` if you want. Generated walk lines assume `held` and `berth` are on `PATH`. Copy walks are `exists DEST` (no `--follow`: the source still holds). Follow walks are `--follow exists OLD`.

Exit codes: `0` a sheaf was found, `1` the trees are identical (or nothing distinguished them), `2` tool error.

Refs may be any tree-ish: `HEAD~1`, a sha, a tag, `:worktree`, `:index`.

## Examples

**1. A file appeared. Cover is `grep FocusRiverView`, not leftover CJK.**

```bash
ditto -C sitbone 14b1d6e^ 14b1d6e
```

```
# ditto 74363dc..14b1d6e  (sitbone)
# sheaf  (shortest set; copy vs follow)
# B   19  grep FocusRiverView                               1 file
held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
```

**2. `cp a.rs b.rs` is copy. `git mv a.rs b.rs` is follow.**

```bash
ditto A B                 # default --copy --follow
ditto --no-copy A B       # dest is a birth (exists)
ditto --no-follow A B     # rename is two exists
```

```
# C   11  copy a.rs → b.rs                                  1 path
held -C repo --rev B --limit 12 exists b.rs

# R   32  follow 'old name.txt' → 'new name.txt'            2 paths
held -C repo --follow --rev B --limit 12 exists 'old name.txt'
berth -C repo --follow --rev B --limit 12 exists 'old name.txt'
```

Same blob still on A and also born on B is **copy**, not follow. Occupancy of the source never died; B grew a holder.

**3. An island vs HEAD. `git log -- PATH` is empty. The sheaf still names the dead type and prints `--full`.**

```bash
ditto -C sitbone 14b1d6e HEAD
ditto --berth --walks -C sitbone 14b1d6e HEAD
```

## Flags that matter

| flag | meaning |
| --- | --- |
| `--held` / `--berth` | pick the walker (default: held, so `ditto A B \| sh` runs occupancy) |
| `--walks` / `--sh` | only command lines |
| `--copy` | same blob still on A and born on B is copy (**default**) |
| `--no-copy` | dest is a birth (`exists dest`) |
| `--follow` | rename is one identity (**default**) |
| `--no-follow` | path existence is identity (two exists) |
| `--full-walks` | force `--full` on every walk |
| `--no-walks` | sheaf only (still comment-prefixed) |
| `--predicates` | also print tell's ranked catalog |
| `--limit N` | max size of the sheaf |
| `--budget N` | max sum of held-string lengths |
| `--json` | `sheaf`, `walks`, `identities`, `unexplained` |
