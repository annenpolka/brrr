# glyph

Shortest covering set of predicates that distinguish two git trees, as ready-to-run `held` / `perch` lines — with **`--follow` so a rename is one identity**.

`tell` lists unary questions. `sheaf` prints a covering set plus walks. `glyph` flips one assumption: **path existence is not identity**. `git mv a.rs b.rs` is one glyph, not `exists a.rs` plus `exists b.rs`.

glyph itself does not walk history. Default stdout is the sheaf (comment-prefixed covering set) plus pasteable occupancy commands. `glyph A B | sh` may run `held`. `--held` / `--perch` pick the walker.

Not `git diff --name-status`. Diff lists letters. glyph names the questions you paste into occupancy.

## Install / run

```bash
# from this directory
./glyph --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `glyph` onto your `PATH` if you want. Generated walk lines assume `held` and `perch` are on `PATH` (and that `held --follow exists PATH` treats a rename as one occupancy).

Exit codes: `0` a sheaf was found, `1` the trees are identical (or nothing distinguished them), `2` tool error.

Refs may be any tree-ish: `HEAD~1`, a sha, a tag, `:worktree`, `:index`.

## Examples

**1. A file appeared. Cover is `grep FocusRiverView`, not leftover CJK.**

```bash
glyph -C sitbone 14b1d6e^ 14b1d6e
```

```
# glyph 74363dc..14b1d6e  (sitbone)
# sheaf  (shortest set; a rename is one identity)
# B   19  grep FocusRiverView                               1 file
held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
```

**2. `git mv` is one follow, not two exists.**

```bash
glyph A B          # default --follow
glyph --no-follow A B
```

```
# R   32  follow 'old name.txt' → 'new name.txt'            2 paths
held -C repo --follow --rev B --limit 12 exists 'old name.txt'
```

`--no-follow` recovers path identity: `exists '*old name*'` and `exists '*new name*'`.

**3. An island vs HEAD. `git log -- PATH` is empty. The sheaf still names the dead type and prints `--full`.**

```bash
glyph -C sitbone 14b1d6e HEAD
glyph --perch --walks -C sitbone 14b1d6e HEAD
```

## Flags that matter

| flag | meaning |
| --- | --- |
| `--held` / `--perch` | pick the walker (default: held, so `glyph A B \| sh` runs occupancy) |
| `--walks` / `--sh` | only command lines |
| `--follow` | rename is one identity (**default**) |
| `--no-follow` | path existence is identity (two exists) |
| `--full-walks` | force `--full` on every walk |
| `--no-walks` | sheaf only (still comment-prefixed) |
| `--predicates` | also print tell's ranked catalog |
| `--limit N` | max size of the sheaf |
| `--budget N` | max sum of held-string lengths |
| `--json` | `sheaf`, `walks`, `identities`, `unexplained` |
