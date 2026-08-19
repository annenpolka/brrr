# mutation-62 — ford

## Primitive

Occupancy of a merge commit is a join of parent statuses, not a boolean
sample on the merge SHA and not connected components of `git log --reverse`.

## Why this might not exist

held, perch, roost, and tenure sample the merge tree. First-parent
`exists CLAUDE.md` on kizu therefore **names the merge** `0ea3916` and hides
the topic birth `e1098c8`. roost v2 annotates origin after the fact; the
era still *starts* at the merge.

stead flipped “a failed probe is FALSE” and compressed `--full` along
parent edges. That is still a boolean on each SHA: the merge is TRUE
because its tree has the file. DESTROYER occupancy already said `--full`
is not the merge lattice.

The missing verb: at a two-parent commit, occupancy **is** `meet`/`join`
of the incoming snapshots. Default meet: TRUE iff all parents TRUE (the
merge *preserves*). `--any`: TRUE if any parent TRUE (the merge
*introduces* via a side). Print the equation. Do not invent a birth.

berth occupies file identity across rename. ford occupies the crossing.

## How to run

```bash
chmod +x ./ford
./ford --help
./ford lattice
./demo.sh
./ford --now -C /tmp/empty-dirty exists README.md
./ford -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./ford --any -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./ford --boolean -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
./ford --full -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone exists Sources/SitboneUI/FocusRiverView.swift
./ford -C /Users/annenpolka/ghq/github.com/annenpolka/skills grep preact-zero-mock
```

Python 3.9+, stdlib only, git. TSV on a pipe, human on a tty, `--json`
for asserts. Exit 0 iff last sample is TRUE, 1 if FALSE, 3 if
UNKNOWN/SHALLOW/EMPTY dominates, 2 error.

## Lattice

Chain (a lattice): `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`.

- **FALSE** — measured absence
- **SHALLOW** — parent or history missing (unmeasured)
- **UNKNOWN** — probe failed (timeout, invalid regex, checkout)
- **EMPTY** — occupied, not as text (binary/NUL)
- **TRUE** — occupied as asked

meet `⊓` (`--all`, default) is inf: TRUE only if every parent is TRUE.
join `⊔` (`--any`) is sup: TRUE if any parent is TRUE.

Join inputs are **parent tree** statuses, not a recursive walk. A missing
parent object is SHALLOW, not FALSE. Timeout on a parent is UNKNOWN, not
FALSE. Occupancy of the merge is the join; `tree=` is a footnote so a
snapshot that has the file is not silently called a birth.

Non-merge commits still sample the tree. A ford (parents disagree, or
tree disagrees with the join) is never compressed into a boolean run.
`--tree` disables the join. `--boolean` downcasts tree TRUE/else-FALSE
to ancestor held. `--list` is `git log --reverse`.

`./ford lattice` prints both 5×5 tables.

## Empirical transcript

### Before the improvement

v1 already had the chain lattice, extra-probe of off-walk merge parents,
ford isolation, `--now` filesystem, SHALLOW grafts, UNKNOWN timeouts.
`./demo.sh` — 84 assertions, exit 0.

Diamond first-parent `--all`: `now=FALSE`, `tree_now=TRUE`, one ford
`FALSE ⊓ TRUE = FALSE`, origin is topic D. `--any` keeps the ford and
sets TRUE (introduced via D). `--tree` / `--boolean` recover held's `FT`
birth at M. `--full --tree --list` is the `FTFT` lie. `--full --all`
TRUE starts on topic C; the merge is a FALSE ford, not a lattice TRUE
component.

Timeout-merge: meet(TRUE, UNKNOWN)=UNKNOWN, exit 3, not FALSE.
`--any` is TRUE ⊔ UNKNOWN = TRUE. Depth-1 stay.txt / missing path /
kizu CLAUDE.md are SHALLOW. sitbone first-parent never_held hints
`--full`; `--full` recovers 11. skills grep still TRUE at HEAD.

kizu first-parent `--all` prints the join and does **not** name
`0ea3916` as birth — but the TRUE era still *starts at the next merge*:

```
$ ./ford -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
FALSE     1 commit    0ea3916
       ford  FALSE ⊓ TRUE = FALSE  (does not preserve)
       parent cbaf29a=FALSE  init: kizu v0.1 skeleton
       parent e1098c8=TRUE   chore: bootstrap CLAUDE.md…
       tree=TRUE  snapshot has it; occupancy is the parent join, not a birth
       origin: e1098c8
TRUE      22 commits  21ae074..9349dc5
       21ae074  Merge pull request #2 from annenpolka/feat/v0.1-mvp
now=TRUE  true=22/24  fords=1  join=all  tree_now=TRUE
```

roost v1 named `0ea3916`. ford v1 names a ford there, then a 22-commit
TRUE run whose *start* is `21ae074` (PR #2, T⊓T preserve). Anyone who
reads era starts as births now thinks CLAUDE.md was born at PR #2.
Same class of lie, one merge later.

### After the improvement

Forced by kizu, not polish. A TRUE run that follows a ford is
`kind=preserve` (if it starts at a merge) or `kind=continue`, with
`continued_from` pointing at the ford and `origin` still `e1098c8`.
Diamond `--full` topic TRUE stays `run` (the ford is later; that *is*
birth on the side).

```
$ ./ford -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
FALSE     1 commit    0ea3916
       ford  FALSE ⊓ TRUE = FALSE  (does not preserve)
       parent cbaf29a=FALSE
       parent e1098c8=TRUE
       tree=TRUE  snapshot has it; occupancy is the parent join, not a birth
       origin: e1098c8
TRUE      22 commits  21ae074..9349dc5
       preserve after ford 0ea3916; not birth
       origin: e1098c8  chore: bootstrap CLAUDE.md…
now=TRUE  true=22/24  fords=1  join=all  tree_now=TRUE
```

`--any` still prints a TRUE *ford* at `0ea3916` (FALSE ⊔ TRUE), not a
23-commit birth. `--boolean` still recovers held's birth at the merge.
Depth-1 is SHALLOW. `./demo.sh` — 88 assertions, exit 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic diamond | parents F/T, merge tree T: `--all` is not birth; `--any` names the topic; `--tree`/`--boolean` recover held's FT |
| merge-added file | F⊓F with tree=TRUE: born in the merge snapshot, not a parent join |
| preserve merge | T⊓T compresses; not a ford |
| timeout parent | meet(T,U)=U, not FALSE |
| empty-dirty `--now` | filesystem TRUE |
| depth-1 clone | SHALLOW, not birth / never-held |
| kizu `exists CLAUDE.md` | first-parent must not name `0ea3916` as birth; ford prints `e1098c8` |
| sitbone `FocusRiverView.swift` | first-parent never; `--full` island 11; depth-1 SHALLOW |
| skills `grep preact-zero-mock` | still TRUE at HEAD; `exists SKILL.md` FALSE |

## Surprises

- kizu first-parent has 18 merges. Only `0ea3916` disagrees on
  `CLAUDE.md` (F/T). The other 17 are T⊓T and compress. The lattice is
  loud only when the merge is actually a crossing.
- sitbone FocusRiverView has **zero** disagreeing merges. The island
  never crossed main. `--full` is still tree occupancy of an island;
  ford has nothing to join. That is correct, not a miss.
- Join inputs have to be parent *trees*, not parent occupancy. Using
  occupancy would feed `0ea3916`'s FALSE join into PR #2 and claim
  T⊓T was F⊓T forever.
- `TRUE ⊔ UNKNOWN = TRUE` and `FALSE ⊔ SHALLOW = SHALLOW` are the
  payload: a timeout/missing parent cannot found a FALSE death.

## Failures

1. **`--boolean` / `--tree` reintroduce the merge-birth lie** by
   design. Labelled lossy.
2. **First-parent TRUE still *spans* `21ae074..HEAD`.** We refuse to
   call it birth; we do not rewrite the span into `e1098c8..HEAD`
   (that SHA is off the first-parent walk).
3. **Octopus is folded meet/join**, documented two-parent lattice.
   No special 3-way display beyond `A ⊓ B ⊓ C = …`.
4. **Rename is still path death.** berth's object, not this one.
5. **`now=FALSE` at a merge HEAD whose tree has the file** under
   `--all`. Honest for preserve; footgun for "does this file exist."
   `tree_now` and `--any`/`--tree` are the exits.

## Suggested mutations

- Recursive join: a merge-parent that is itself a merge contributes
  its occupancy, not its tree.
- Pipe `ford --json` into roost to split holders on a still-TRUE join.
- Cache `(tree, predicate) → status` so extra parent probes are free.
- `--follow` is berth, not this object.
- Refuse `--boolean` when any parent is not T/F, instead of downcasting.

## Flipped assumption: bought and lost

Parents assumed **occupancy of a merge is occupancy of the merge SHA**.

**Bought**

- A disagreeing merge is a printed join, not a birth.
- `--all` vs `--any` is a real lattice, not two list compressors.
- SHALLOW parent ≠ FALSE parent; timeout parent ≠ FALSE parent.
- The TRUE run after a ford is named preserve/continue, not birth at
  the next merge (kizu `21ae074`).
- `--boolean` / `--tree` recover held on purpose.

**Lost**

- `now=FALSE` at a merge HEAD whose *tree* has the file (join=all).
  `tree_now` is the snapshot; occupancy is the crossing.
- First-parent TRUE after an introducing merge starts at the next
  preserving commit, not at the topic SHA (the ford names that SHA).

## Kill / keep

**Keep.** The occupancy verb was already real. This mutation is the
merge algebra DESTROYER asked for and roost could only footnote. The
v1→v2 change was forced by kizu: refusing birth at `0ea3916` still
left birth-shaped TRUE starting at `21ae074`. Not polish.
