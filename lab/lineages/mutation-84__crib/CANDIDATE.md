# mutation-84 — crib

## Primitive

Occupy **new holder of this blob**. `copy SRC` / `exists SRC` is TRUE while a dest exists that was born as a copy of SRC (source still held at birth). `git mv` remains FOLLOW.

## Why this might not exist

ditto emits covering predicates that distinguish copy from follow, then pastes `held exists DEST`. held does not parse `--follow`; copy occupancy is not a first-class verb. berth `--follow` occupies the file that moved (A name gone). held `exists DEST` is TRUE for a unique birth, a follow dest, and a copy dest alike.

The recurring annoyance: you are staring at `src/init/install.rs` and occupancy tools cannot say *this dest is an extra holder of `src/init.rs`'s blob*. They can say the dest exists, or that some other path moved.

Discarded as too conventional: wrapping `git diff -C` / `git log --find-copies`, adding a copy letter to glyph, stuffing `--copy` onto berth so identity occupancy grows a third ambit.

## How to run

```bash
./crib --help
./demo.sh 0
./crib exists a.rs
./crib copy a.rs
./crib -C /path/to/repo --full exists src/init.rs
./crib -C /path/to/repo --full exists src/init/install.rs
./crib -C /path/to/repo --full exists docs/deep-research-ai-agent-hooks.md
```

Python 3.9+, stdlib only, `git`. Exit 0 iff a crib dest holds at the last sample.

## Empirical transcript

### Before the improvement

v1 walks each commit against its first parent. Exact SHA remaining-holder is COPY. Exclusive-side same SHA with no remaining holder is FOLLOW. Similarity copies compare dest-on-B to source-on-A (COPY_SIM_MIN 0.5, related paths).

**Exact `cp a.rs b.rs` (both exist):**

```
# exists a.rs
       copy: a.rs → b.rs
FALSE  1 commit
TRUE   2 commits  holders: b.rs
now=TRUE
```

Query dest `exists b.rs` is the same roost. `git mv 'old name.txt' 'new name.txt'` is never cribbed; hint names berth `--follow`.

**Remaining blob:** `a.rs` and `twin.rs` share a SHA; delete twin, `cp a.rs b.rs`:

```
copy a.rs → b.rs
# not follow twin.rs → b.rs
```

**Extract-and-edit** (source emptied, dest holds the extracted lines): dest-on-B vs source-on-A Jaccard 0.91. Copy, not unique birth.

**kizu R100** `--full` is FOLLOW, not COPY:

```
$ ./crib -C kizu --full exists docs/deep-research-ai-agent-hooks.md
FALSE  244 commits
hint: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md is a follow (A name gone), not a copy.
      berth --follow exists deep-research-ai-agent-hooks.md
```

**sitbone** FocusRiverView `--full` is a unique birth (`held exists`), never cribbed.

**kizu C056** `--full` is the copy (dest-on-B vs source-on-A Jaccard 0.551):

```
$ ./crib -C kizu --full exists src/init.rs
       copy: src/init.rs → src/init/install.rs
TRUE   12 commits  5671a72..9349dc5  holders: src/init/install.rs
now=TRUE  true=12/244
```

**kizu C056 first-parent is a miss.** Merge 243c46e vs first parent: dest born, source remains, Jaccard 0.195 < 0.5. Occupancy never-held. dest-on-B vs source-on-A at 5671a72 is 0.551 — off the mainline.

```
$ ./crib -C kizu exists src/init.rs
FALSE  24 commits
hint: never cribbed on first-parent, but dest src/init/install.rs was copied from src/init.rs
      off the mainline (5671a72). rerun with --full
```

`held exists src/init/install.rs` is TRUE 5/24 from the merge. crib first-parent cannot yet say the dest is a crib dest.

### After the improvement

Forced by that first-parent miss, not polish. Dest born at a merge is classified at dest's actual add (`git log --diff-filter=A`), dest-on-B vs source-on-A at 5671a72. Occupancy on first-parent is dest existence from the merge; origin names the copy.

```
$ ./crib -C kizu exists src/init.rs
       copy: src/init.rs → src/init/install.rs
FALSE  19 commits  cbaf29a..b4e6a5d
TRUE    5 commits  243c46e..9349dc5
       origin: 5671a72  refactor: split init installers  as src/init/install.rs
       holders: src/init/install.rs
now=TRUE  true=5/24
```

Same command on dest `src/init/install.rs` is the same roost (`true=5`). `held exists src/init/install.rs` is also TRUE 5/24 — but that is dest path occupancy, TRUE for a unique birth too. crib is TRUE because dest was cribbed, and names the source.

`--full` is still TRUE 12/244 from 5671a72. R100 dest is still FOLLOW. sitbone FocusRiverView is still a unique birth.

`./demo.sh 0` — 49 assertions. Exit 0.

## Dogfood targets

- synthetic fixture: `cp a.rs b.rs` vs `git mv`; remaining-blob twin; dest death; extract-and-edit; `計画.md`; nested git; `--now`; empty repo
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — recorded copy `5671a72` (`C056 src/init.rs → src/init/install.rs`, blob still at source) vs R100 follow into `docs/`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView unique birth; cover stays `grep FocusRiverView`

## Surprises

- Exclusive-side same-SHA is not enough to decide follow. If any shared path still holds the blob, the dest is a new holder.
- dest-on-B vs source-on-A is the extract-and-edit number. kizu B-vs-B Jaccard is 0.04; A-vs-B is 0.551.
- First-parent merge Jaccard for install.rs vs mainline `init.rs` is 0.195 — below 0.5. The copy event is 5671a72 on the topic branch. Adjacent first-parent trees are the wrong pair.
- Query dest or source: same copy roost. `held exists DEST` is also TRUE for unique births and follow dests; crib is not.

## Failures

- v1 first-parent missed kizu C056 (merge Jaccard 0.195). v2 origin-behind-merge: dest add is 5671a72, occupancy TRUE 5/24 from the merge, origin names the copy.
- Copy+later-delete of dest ends occupancy even if source still holds (correct: the extra holder is gone).
- Similarity copies can glue coincidentally similar new files that share an extension. Related-path + changed-source scoring is the hedge.
- `--now` hashes the worktree; a dirty identical blob is an extra holder.

## Suggested mutations

- `ditto A B | crib` so the covering copy glyph is occupancy-in, eras-out, without `sh`.
- `--code` grain so dest boilerplate does not pair unrelated extracts.
- Query-restricted similarity at fat merges (first-parent kizu still Jaccard-scans every leftover dest).

## Flipped assumption: bought and lost

Parent ditto assumed **copy is a covering predicate between two trees**, pasted as `held exists DEST`.

**Bought**

- `cp a.rs b.rs` is occupancy of dest as extra holder, from source or dest name.
- `git mv` is never cribbed; hint names berth `--follow`.
- Remaining blob cannot be a follow of the exclusive twin.
- kizu `--full` C056 is one copy roost (`true=12`); first-parent dest occupancy is TRUE 5/24 with origin 5671a72; R100 is follow; sitbone FocusRiverView stays a unique birth.

**Lost**

- Unary path occupancy of DEST (`held exists DEST`) no longer answers the question: dest existence is not crib-ness.
- First-parent pairwise Jaccard is not the copy event when the extract happened off the mainline.

## Kill / keep

**Keep.** It is not `git diff -C` and it is not glyph with a copy letter. On the first remaining-blob fixture it refused follow; on the first real R100 it still refused copy; on the first real recorded copy (`C056`, blob still at `src/init.rs`) `--full` named `copy src/init.rs → src/init/install.rs` and v2 first-parent was forced to TRUE 5/24 with origin 5671a72. Sitbone stayed `held exists` / `grep FocusRiverView`. Copy vs follow is empirically distinct.
