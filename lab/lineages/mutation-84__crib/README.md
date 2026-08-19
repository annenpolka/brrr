# crib

Occupancy of a **new holder of this blob**.

`held exists SRC` is path occupancy. `berth --follow exists SRC` is rename identity (A name gone). `ditto` emits copy vs follow but does not walk. crib occupies **COPY**: dest is a new path whose blob (or similar dest) lived at SRC on A.

`git mv` remains FOLLOW. `cp` is COPY (both names exist). Query the source or the dest; occupancy is the extra dest.

Not `git diff -C`. Not glyph with a copy letter. Not a third ambit.

## Install / run

```bash
# from this directory
./crib --help
./demo.sh 0
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `crib` onto your `PATH` if you want.

Exit codes: `0` a crib dest holds at the last sample, `1` it does not, `2` tool error.

`copy PATH` and `exists PATH` are the same observer. `--follow` is rejected (that is berth's verb).

## Examples

**1. `cp a.rs b.rs` is one crib. `git mv` is not.**

```bash
crib exists a.rs
crib copy a.rs
crib exists b.rs
crib exists 'old name.txt'
```

```
# exists a.rs  (repo, 3 commits, first-parent, copy)
       copy: a.rs → b.rs
FALSE  1 commit
TRUE   2 commits  holders: b.rs
now=TRUE  true=2/3
```

`exists 'old name.txt'` after `git mv` is never cribbed: A name gone is FOLLOW. Hint points at `berth --follow exists 'old name.txt'`.

**2. A recorded copy with the source still holding (kizu C056).**

```bash
crib --full exists src/init.rs
crib --full exists src/init/install.rs
```

Git recorded `C056 src/init.rs → src/init/install.rs`. dest-on-B vs source-on-A Jaccard is 0.55; B-vs-B is 0.04. Occupancy is the extra dest, from either name.

`--full` is TRUE from 5671a72 (12 commits). First-parent dest occupancy starts at the merge; origin names the copy:

```
copy: src/init.rs → src/init/install.rs
TRUE   5 commits  holders: src/init/install.rs
       origin: 5671a72  refactor: split init installers
```

The same dest after `git mv` into `docs/` (kizu R100) is FOLLOW, never cribbed.

**3. A unique birth is not a crib dest.**

```bash
crib --full exists Sources/SitboneUI/FocusRiverView.swift
```

FocusRiverView is an island `held` already covers. crib is never-held and hints `held exists PATH`. Cover stays `grep FocusRiverView`.
