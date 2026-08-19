# mutation-94 — pup

## Primitive

Covering predicates in; occupancy eras out. `ditto A B | pup` occupies COPY vs FOLLOW without `sh`. `git mv` is FOLLOW; `cp` is COPY.

## Why this might not exist

ditto emits covering predicates that distinguish copy from follow, then pastes `held exists DEST` / `--follow exists OLD`. `ditto A B | sh` is paste. held does not parse `--follow`. dest existence is TRUE for a unique birth, a follow dest, and a copy dest alike. crib occupies `copy SRC` / `exists SRC` as a unary query and does not read the pipe. berth occupies identity and does not read the pipe.

The recurring annoyance: you are staring at a ditto sheaf (`copy src/init.rs → src/init/install.rs`) and occupancy still wants you to pick a walker, paste a line, and remember that the walk is dest existence not crib-ness.

Discarded as too conventional: wrapping `git diff -C`, growing a third ambit, stuffing `--stdin` onto crib so unary copy occupancy grows a pipe flag.

## How to run

```bash
./pup --help
./demo.sh 0
ditto A B | ./pup
ditto --walks A B | ./pup
./pup -C /path/to/repo A B
./pup -C /path/to/repo --full 5671a72^ 5671a72
```

Python 3.9+, stdlib only, `git`. Exit 0 iff a covering dest holds at the last sample. `ditto` is optional (`pup A B` classifies two trees).

## Empirical transcript

### Before the improvement

v1 parses ditto/held/berth covering lines (sheaf comments, JSON, `--walks`) and occupies dest existence for COPY, identity for FOLLOW. `pup A B` is ditto invoked internally. Remaining-blob exclusive SHA is copy of the living holder. Extract-and-edit is dest-on-B vs source-on-A.

**Exact `cp a.rs b.rs` then dest death (`ditto T0 T1 | pup`):**

```
# copy a.rs → b.rs
FALSE  1 commit
TRUE   2 commits  holders: b.rs
now=FALSE  true=2/6
```

**`git mv 'old name.txt' 'new name.txt'` is FOLLOW, never COPY.**

**kizu C056** `ditto 5671a72^ 5671a72 | pup` is the pipe, not paste:

```
$ ditto -C kizu 5671a72^ 5671a72 | ./pup -C kizu
# copy src/init.rs → src/init/install.rs  (kizu, 24 of 244 commits, first-parent, copy)
       copy: src/init.rs → src/init/install.rs
FALSE  19 commits  cbaf29a..b4e6a5d
TRUE    5 commits  243c46e..9349dc5
       holders: src/init/install.rs
now=TRUE  true=5/24
```

`--full` is TRUE 12. `ditto --walks` (the paste `sh` would run: `held exists src/init/install.rs`) recovers the copy and names the source.

**First-parent origin is missing.** Dest occupancy starts at merge `243c46e`. The copy event is `5671a72` on the topic branch. v1 dest existence is the right boolean and the wrong event.

**kizu R100** is FOLLOW (`true=21/24` first-parent), not COPY.

**sitbone** `ditto 14b1d6e^ 14b1d6e | pup` is grep FocusRiverView — no copy/follow. Hint: held.

`./demo.sh 0` — 43 assertions. Exit 0.

### After the improvement

Forced by that first-parent miss, not polish. Dest occupancy that starts at a merge names dest's actual add (`git log --diff-filter=A`). kizu C056 dest-on-B vs source-on-A at 5671a72 is the copy; first-parent dest existence is TRUE 5/24 from the merge; origin names the covering event.

```
$ ditto -C kizu 5671a72^ 5671a72 | ./pup -C kizu
# copy src/init.rs → src/init/install.rs  (kizu, 24 of 244 commits, first-parent, copy)
       copy: src/init.rs → src/init/install.rs
FALSE  19 commits  cbaf29a..b4e6a5d
TRUE    5 commits  243c46e..9349dc5
       origin: 5671a72  refactor: split init installers
                as src/init/install.rs
       holders: src/init/install.rs
now=TRUE  true=5/24
```

`--full` is still TRUE 12/244 from 5671a72. R100 dest is still FOLLOW (`true=21/24` first-parent; origin `4e37f16` is the covering rename, not berth's identity birth `321a830`). sitbone FocusRiverView is still grep-only.

`--walks` C056 (`held exists src/init/install.rs`, the paste `sh` would run) still recovers `copy src/init.rs → src/init/install.rs`.

`./demo.sh 0` — 44 assertions. Exit 0.

## Dogfood targets

- synthetic fixture: `cp a.rs b.rs` vs `git mv`; remaining-blob twin; dest death; extract-and-edit; `計画.md`; nested git; `--now`; empty repo; `ditto | pup` and `ditto --walks | pup`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — recorded copy `5671a72` (`C056 src/init.rs → src/init/install.rs`) vs R100 follow into `docs/`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView unique birth; cover stays `grep FocusRiverView`

## Surprises

- The paste `held exists DEST` is not the covering. `--walks` C056 has no copy glyph; classifying dest at `rev^..rev` recovers `copy src/init.rs → src/init/install.rs`.
- Occupancy tip is HEAD, not ditto's `--rev` covering event. dest existence through first-parent is TRUE 5/24 from the merge even when the covering was classified at 5671a72.
- Exclusive-side same-SHA is still COPY of the living holder (remaining blob). git `--find-renames` is only used to walk FOLLOW identity, never to classify a copy (`-C` stays dead).

## Failures

- v1 first-parent C056 dest occupancy was TRUE 5/24 with origin missing. v2 dest-add behind the merge names 5671a72. `--no-origin` is the v1 boolean.
- Copy dest later `git mv`'d is dest-path death under v1 dest existence (crib follows dest identity).
- Similarity copies can still glue coincidentally similar new files that share an extension when `pup A B` classifies. Related-path + changed-source scoring is the hedge.

## Suggested mutations

- Occupy dest identity after a later `git mv` of the copy dest (v1 dest existence dies with the old dest path).
- `--code` grain so ditto dest boilerplate does not sit next to the copy covering we occupy.
- `ditto A B | pup --now` so an uncommitted extra holder of a covering dest is a sample without a second covering classify.

## Flipped assumption: bought and lost

Parent crib assumed **copy occupancy is a unary path query**. Parent ditto assumed **the pipe is paste (`| sh`)**.

**Bought**

- `ditto A B | pup` is eras-out without `sh`.
- `--walks` dest-exists paste recovers COPY vs unique birth vs FOLLOW.
- `git mv` covering is identity eras; `cp` covering is dest extra-holder eras.
- kizu C056 first-parent `true=5` with origin 5671a72; `--full` `true=12`; R100 is follow (origin 4e37f16, the covering rename); sitbone stays grep.

**Lost**

- Unary `held exists DEST` no longer answers the question: dest existence is occupancy of a covering, not crib-ness by itself.
- First-parent dest boolean is not the copy event when the extract happened off the mainline.

## Kill / keep

**Keep.** It is not `git diff -C` and it is not crib with `--stdin`. On the first remaining-blob fixture it refused follow; on the first real R100 it still refused copy; on the first real recorded copy (`C056`) `ditto | pup` named `copy src/init.rs → src/init/install.rs` and v2 first-parent was forced to TRUE 5/24 with origin 5671a72. Sitbone stayed `grep FocusRiverView`. The pipe is eras-out without `sh`.
