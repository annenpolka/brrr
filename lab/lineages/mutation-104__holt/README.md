# holt

Occupancy of a **file identity**, from all reachable R records.

berth claimed: query the old name or the new name, occupancy stays TRUE. That is false on berth's default first-parent walk (the merge added dest as A, no R on mainline). Default `exists PATH` at a living leftover name occupied the *other* file.

`holt` defaults to every reachable commit (`--first-parent` is opt-in). Identity is resolved from all reachable R records even on a first-parent occupancy walk. `exists PATH` occupies **this** path's identity at the walk tip, not the leftover twin that moved away.

`--no-follow` is path occupancy. `--boolean` is ancestor `held`. A copy is not a rename. A leftover-blob C record is not a follow.

## Install / run

```bash
# from this directory
./holt --help
./demo.sh 0
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `holt` onto your `PATH` if you want.

Exit codes: `0` predicate holds at the last sample (HEAD, or the working tree with `--now`), `1` it does not, `2` tool error.

Default: exact `exists` follows; occupancy walks every reachable commit.

## Examples

**1. Query the dead name or the dest; occupancy stays TRUE.** (spaces rename)

```bash
holt exists 'old name.txt'
holt exists 'new name.txt'
holt --no-follow exists 'old name.txt'
holt --first-parent exists 'old name.txt'
```

```
identity: old name.txt → new name.txt
TRUE  3 commits  holders: old name.txt
TRUE  4 commits  holders: new name.txt
       + new name.txt
       - old name.txt
now=TRUE  eras=2  boolean=1  holder_splits=1
```

`--no-follow` on the old name is a path death (TF). `--first-parent` still stitches old→dest from all-reachable R when the merge hid the letter.

**2. A real rename is one roost from either name, without `--full`.** (kizu)

```bash
holt exists docs/deep-research-ai-agent-hooks.md
holt exists deep-research-ai-agent-hooks.md          # dead name; same roost
holt --no-follow exists deep-research-ai-agent-hooks.md
holt --first-parent exists deep-research-ai-agent-hooks.md
```

Default (all reachable): TRUE 187 from either name, kinds `birth/move`. `--no-follow` on the old path: TRUE 13 then FALSE 174. `--first-parent` from either name: TRUE 21 after the merge, origin `321a830 as deep-research-ai-agent-hooks.md`.

**3. A leftover name is this path's identity, not the twin.** (recreate after `git mv`)

```bash
holt exists old.txt     # reincarnation at old.txt; does not follow to new.txt
holt exists new.txt     # the file that moved
holt exists a.txt       # after a serialized name-swap: the occupant now named a
```

`git mv old.txt new.txt` then recreate `old.txt`: `exists old.txt` is a new roost (the leftover). `exists new.txt` is `old.txt → new.txt`. Two files swapping names: `exists a.txt` occupies the file sitting at `a.txt`, not the original AAA that now lives at `b.txt`. `--now exists DEST` of an uncommitted `git mv` occupies dest (same roost as the old name); a dirty leftover at the old name is this path, not the twin.
