# DESTROYER — ford

Adversarial pass on **ford's merge occupancy lattice** (join of parent
*trees*, not a boolean sample on the merge SHA). No rewrites: the
failures are conceptual. DESTROYER occupancy already said `--full` is
not the lattice — cite only, not re-run. This pass is the lattice
itself.

- **ford** (mutation-62, v2) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb2e776f004a`
- Peel: **weir** (mutation-86, recursive join) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-109aeaf41ba5`
- Transcript: `/tmp/destroy-ford/transcript.txt`
- Fixtures: `/tmp/destroy-ford/fixtures/{diamond,octopus-1of3,octopus-2of3,merge-of-merges,nested-merges,rename,timeout-merge,binary,merge-added,kizu-shallow,sitbone-shallow}`
- Attack driver: `/tmp/destroy-ford/attack.py`
- `./demo.sh` still **PASS=88 FAIL=0** after the attacks. `ford --help` rc=0.

Attacks: octopus folds, `--boolean` downcast, first-parent TRUE spanning
`21ae074`, birth at `0ea3916`, rename as path death, `now=FALSE` at a
merge HEAD whose tree has the file, merge-of-merges reprinting nested
lattice.

Verdict: **mutate, do not kill.** kizu `CLAUDE.md` at `0ea3916` is still
`FALSE ⊓ TRUE`, origin still `e1098c8`, not a boolean birth. sitbone
`FocusRiverView.swift` first-parent still never-held and hints `--full`;
`--full` still recovers the 11-commit island `git log -- PATH` cannot
see. The attacks show where the join is parent *trees* (so PR #2 is
`T⊓T` preserve), where `--boolean` never computes the lattice, and
where a three-parent meet cannot tell 1-of-3 from 2-of-3.

---

## Primitive restated

Occupancy of a merge is a join of parent statuses, not a boolean sample
on the merge SHA and not connected components of `git log --reverse`.

| flag | lattice | TRUE at a merge when |
| --- | --- | --- |
| default (`--all`) | meet `⊓` | **every** parent is TRUE (the merge *preserves*) |
| `--any` | join `⊔` | **any** parent is TRUE (the merge *introduces* via a side) |

Join inputs are **parent trees**, not parent occupancy. A merge whose
parents disagree is printed as a **ford**. A later TRUE run is
`preserve`/`continue` after that ford, not a birth at the next merge.
`--tree` samples the merge SHA like held. `--boolean` is labelled held
recovery. Chain: `FALSE ⊑ SHALLOW ⊑ UNKNOWN ⊑ EMPTY ⊑ TRUE`.

weir (the peel this pass is not rewriting) joins parent *occupancy*
when a parent is itself a merge.

DESTROYER occupancy ([`lab/judges/DESTROYER_OCCUPANCY.md`](DESTROYER_OCCUPANCY.md)):
held/perch/tenure compress `git log --reverse`; `--full` invents a
FALSE gap on a diamond; kizu first-parent **names the merge** `0ea3916`
and hides topic birth `e1098c8`. ford exists because of that. Not
re-probed here except where they hit the lattice (`--boolean` restoring
held; rename as path death).

---

## 1. Octopus folds — 1-of-3 and 2-of-3 are the same meet (conceptual)

Three-parent merge `git merge t1 t2` from a root that does not have
`src/app.py`. Two occupancy patterns. Documented two-parent lattice;
no special 3-way display beyond `A ⊓ B ⊓ C`.

**1-of-3** (only t1 has the file):

```
$ ./ford -C octopus-1of3 exists src/app.py
FALSE     1 commit   34d2ba7
       A root no occupancy
FALSE     1 commit   6f34cdd
       M octopus t1 t2
       ford  FALSE ⊓ TRUE ⊓ FALSE = FALSE  (does not preserve)
       parent 34d2ba7=FALSE  A root no occupancy
       parent 4eb307e=TRUE   T1 has occupancy
       parent 3f27a08=FALSE  T2 no occupancy
       tree=TRUE  snapshot has it; occupancy is the parent join, not a birth
       origin: 4eb307e  T1 has occupancy  (TRUE parent)
now=FALSE  true=0/2  fords=1  tree_now=TRUE  never_held=True
# rc=1
```

**2-of-3** (t1 and t2 both have the file):

```
$ ./ford -C octopus-2of3 exists src/app.py
       ford  FALSE ⊓ TRUE ⊓ TRUE = FALSE  (does not preserve)
       parent 34d2ba7=FALSE  A
       parent 4eb307e=TRUE   T1 has occupancy
       parent 3df3acb=TRUE   T2 has occupancy
       origin: 4eb307e  T1 has occupancy  (TRUE parent)
now=FALSE  true=0/2  fords=1  tree_now=TRUE  never_held=True
# rc=1
```

Meet inf is FALSE as soon as **any** parent is FALSE. Majority does not
exist. 1-of-3 and 2-of-3 are the same occupancy, the same exit, the
same `never_held`. `--any` is TRUE for both (`FALSE ⊔ TRUE ⊔ FALSE` and
`FALSE ⊔ TRUE ⊔ TRUE`) — also indistinguishable as occupancy.

Origin is the **first TRUE parent** in parent order. 2-of-3 has two
introducing sides; only `4eb307e` (t1) is named. t2 is a parent line
and then dropped.

weir on the same octopus is the same fold (`FALSE ⊓ TRUE ⊓ FALSE`,
`weirs=1`). Recursive join does not invent a 3-way. The hole is the
lattice arity, not the recursion.

---

## 2. `--boolean` downcast — not a downcast of the lattice (conceptual, load-bearing)

`--boolean` is documented as “lossy held recovery: tree TRUE stays,
everything else is FALSE.” CANDIDATE named it labelled loss. Empirically
it is **held**, not a projection of the printed join.

`apply_join` returns the tree sample and skips the parents when
`boolean=True`. Horizon rewrite is also skipped (`if not args.boolean`).
Then `booleanize` maps non-TRUE trees to FALSE. Diamond `--boolean`:

```
fords=0  kinds=['run','run']  joins=[None, None]  now=TRUE
# --boolean is held, not a downcast of FALSE ⊓ TRUE = FALSE
```

No ford era. No equation. TRUE starts at the merge — the occupancy lie
ford exists to refuse.

### Timeout UNKNOWN → FALSE death (weir refuses)

Timeout-merge (slow parent, `--timeout 0.2`):

```
$ ./ford --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
TRUE      1 commit   8926ef6  A fast
UNKNOWN   1 commit   0a6d4f5  M timeout parent
       ford  TRUE ⊓ UNKNOWN = UNKNOWN  (does not preserve)
now=UNKNOWN  # rc=3

$ ./ford --boolean --timeout 0.2 exec -- …
TRUE      1 commit   8926ef6  A fast
FALSE     1 commit   0a6d4f5  M timeout parent
now=FALSE  tree_now=UNKNOWN  # rc=1
warning: --boolean collapsed UNKNOWN/SHALLOW/EMPTY into FALSE (held recovery)

$ ./weir --boolean --timeout 0.2 exec -- …
weir: --boolean would downcast UNKNOWN to FALSE; that is a labelled lie. refuse.
# rc=2
```

ford warns and still does it. Exit 1 is occupancy death. weir's peel
is a refuse.

### EMPTY → FALSE

`grep TOKEN_BIN` after the text copy is deleted, NUL still in
`secret.bin`: `--all` is `TRUE / EMPTY`, rc=3. `--boolean` is
`TRUE / FALSE`, rc=1, `tree_now=EMPTY`. Binary occupancy becomes a
historical FALSE.

### SHALLOW horizon skipped — silent birth / silent never-held

kizu `git clone --depth 1`. Without `--boolean`, ford's own fix holds:

```
$ ./ford -C kizu-shallow exists CLAUDE.md
SHALLOW   1 commit   9349dc5
now=SHALLOW  # rc=3   (not birth, not never-held)
```

`--boolean` skips the horizon, samples the tree, downcasts nothing
because the tree is TRUE:

```
$ ./ford --boolean -C kizu-shallow exists CLAUDE.md
TRUE      1 commit   9349dc5  release: v0.7.0
now=TRUE  true=1/1  walk=first-parent+boolean
# rc=0   warnings=[]
```

Birth at HEAD of a depth-1 clone. No collapse warning — trees were
T/F, so the UNKNOWN/SHALLOW/EMPTY guard does not fire. Occupancy
DESTROYER's held lie, restored by the flag that claims to recover held
on purpose.

sitbone depth-1 `exists FocusRiverView.swift` (file absent from HEAD):

| flag | now | never_held | warning |
| --- | --- | --- | --- |
| `--all` | SHALLOW rc=3 | false | SHALLOW hint |
| `--boolean` | FALSE rc=1 | **true** | none |

A graft with no file becomes “never held,” which is the occupancy
shallow-clone lie ford already refused.

kizu `--boolean` (full clone) does not warn either: every tree is T/F,
so collapse is silent even while it names `0ea3916` as birth.

---

## 3. First-parent TRUE spanning `21ae074` — the tree-join lie (conceptual, load-bearing)

kizu gold SHAs (first-parent walk, 24 of 244):

| SHA | what |
| --- | --- |
| `cbaf29a` | init; tree has no `CLAUDE.md` |
| `e1098c8` | topic birth (`chore: bootstrap CLAUDE.md…`); off first-parent |
| `0ea3916` | Merge PR #1; parents `cbaf29a` `e1098c8` |
| `21ae074` | Merge PR #2; parents `0ea3916` `429e4ac` (both **trees** TRUE) |
| `d9b9645` | first non-merge after the PR #3–#6 cascade |
| `9349dc5` | HEAD `release: v0.7.0` |

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
       21ae074  Merge pull request #2 from annenpolka/feat/v0.1-mvp
       preserve after ford 0ea3916; not birth
       origin: e1098c8
now=TRUE  true=22/24  fords=1  join=all  tree_now=TRUE
```

JSON of the TRUE era: `kind=preserve`, `join=TRUE ⊓ TRUE = TRUE`,
parents `[('0ea3916','TRUE'), ('429e4ac','TRUE')]`. `0ea3916` contributes
its **tree** (TRUE), not its occupancy (`FALSE ⊓ TRUE = FALSE`). The
footnote says “not birth.” The span is still PR #2 → HEAD. Anyone who
reads era starts as births now thinks `CLAUDE.md` was born at PR #2 —
same class of lie DESTROYER occupancy named at `0ea3916`, one merge
later. CANDIDATE v2 bought the footnote and kept the span.

`--any` still a TRUE *ford* at `0ea3916` (`FALSE ⊔ TRUE`), then the same
22-commit preserve starting `21ae074`. Not a 23-commit birth. The
introducing crossing is honest; the next merge is still tree-join
preserve.

weir peel on the same gold:

```
$ ./weir -C kizu exists CLAUDE.md
FALSE     1 commit    0ea3916
       weir  FALSE ⊓ TRUE = FALSE
       refuse birth: a parent already held TRUE
FALSE     1 commit    21ae074
       weir  FALSE ⊓ TRUE = FALSE  (recursive: merge-parent contributes occupancy, not tree)
       parent 0ea3916=FALSE  occupancy  FALSE ⊓ TRUE = FALSE  (tree=TRUE)
              parent cbaf29a=FALSE  tree
              parent e1098c8=TRUE   tree
       parent 429e4ac=TRUE   tree
FALSE     4 commits   ca0577a..ad6de10
       inherited weir 21ae074
TRUE     17 commits   d9b9645..9349dc5
       continue after weir 21ae074; not birth
       origin: e1098c8
now=TRUE  true=17/24  weirs=6
```

Recursive occupancy at `21ae074` is `FALSE ⊓ TRUE = FALSE`. TRUE starts
at the first non-merge (`d9b9645`), not at PR #2. ford's preserve span
is exactly the hole weir exists to name. This pass does not rewrite
ford into weir.

`--full` (lattice walk, not first-parent): TRUE `run` at `e1098c8` (the
topic birth, kind=run, not preserve), ford at `0ea3916`, then
`continue` 241 commits from `2b8b1c1`. The topic SHA is on the walk, so
the birth is nameable. First-parent cannot put `e1098c8` in the span
without rewriting history into a different object.

---

## 4. Birth at `0ea3916` — `--tree` / `--boolean` recover held (labelled, confirmed)

```
$ ./ford --tree -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
TRUE     23 commits   0ea3916..9349dc5
now=TRUE  true=23/24  fords=0  walk=first-parent+tree

$ ./ford --boolean -C kizu exists CLAUDE.md
FALSE     1 commit    cbaf29a
TRUE     23 commits   0ea3916..9349dc5
now=TRUE  true=23/24  fords=0  walk=first-parent+boolean
# warnings=[]   (every tree is T/F; collapse is silent)
```

held's merge-birth, byte for byte. `--boolean` on kizu is not “lossy
lattice”; it is the occupancy DESTROYER already broke, with a walk
tag. weir `--boolean` on the same gold also recovers `0ea3916` but
prints `warning: --boolean is a labelled lie`. ford prints nothing.

Merge-added file (`F⊓F` with `tree=TRUE`, born in the snapshot):

```
$ ./ford exists new.txt
FALSE  ford  FALSE ⊓ FALSE = FALSE  tree=TRUE  born in the merge snapshot
now=FALSE  never_held=True  # rc=1

$ ./ford --boolean exists new.txt
TRUE   1 commit   a998242  M adds new.txt neither parent had
now=TRUE  # rc=0
```

The one case where the merge *is* a birth (`ford_reason=tree`),
`--boolean` is the honest snapshot — and it is indistinguishable from
the introducing-merge lie at `0ea3916`. One flag, two objects.

---

## 5. Rename is path death — berth's object, not this one (conceptual)

Fixture: `old.txt` → `new name.txt` → `計画.md`, then a merge that
keeps the CJK path.

```
$ ./ford exists old.txt
TRUE   1 commit    70d886d  birth old.txt
FALSE  4 commits   25a2d6d..a77a828
now=FALSE  true=1/5

$ ./ford exists 'new name.txt'
FALSE / TRUE 1 / FALSE 3     now=FALSE

$ ./ford exists 計画.md
FALSE 2 / TRUE 3             now=TRUE

$ ./ford grep TOKEN_RENAME
TRUE   5 commits  70d886d..a77a828
       witnesses: old.txt, 計画.md
now=TRUE  true=5/5  fords=0
```

`exists` is path identity. A rename is death plus birth. Spaces and CJK
round-trip via `cat-file` (`core.quotepath=false`). `grep` is content
occupancy across the move; witnesses union the old path and the new.
No `--follow`. weir `--follow` is a refuse (`berth, not this object`).
ford has no such refuse — `--follow` is not a flag. Same hole, quieter.

The merge at the end is `T⊓T` on `計画.md` and compresses. Rename never
becomes a ford. File identity across a crossing is unaskable here.

DESTROYER occupancy already showed three tools, three objects on
rename. Not re-run as a family. Confirmed ford is still `exists`-as-path.

---

## 6. `now=FALSE` at a merge HEAD whose tree has the file (conceptual)

Diamond (dates force first-parent `A B M`; topic `C D` off-walk):

```
$ git cat-file -e HEAD:src/app.py   # true — the blob is in the snapshot

$ ./ford exists src/app.py
FALSE     2 commits  00ca863..5ebdb98
FALSE     1 commit   a76c55c
       ford  FALSE ⊓ TRUE = FALSE
       tree=TRUE  snapshot has it; occupancy is the parent join, not a birth
now=FALSE  true=0/3  fords=1  tree_now=TRUE  never_held=True
# rc=1
hint: HEAD tree is TRUE but occupancy is the parent join (FALSE).
hint: never held on first-parent, but existed in 3 reachable commits off the mainline
```

Exit 1. `never_held=True`. The file is in `HEAD`. Occupancy of the
crossing is honest for *preserve*; it is a footgun for “does this file
exist.” `tree_now` and the hint are the exits. Anyone reading
`never_held` as “this path never occupied the repo” is lied to by a
flag occupancy already trained people to trust.

`--any` is `now=TRUE` (introduce-via-side). `--tree` / `--boolean` are
held's `FT` birth at `M`. Three answers, one path. Default is the join.

Same shape on octopus (both 1-of-3 and 2-of-3) and on merge-added
(`F⊓F` tree TRUE): `never_held=True` while `tree_now=TRUE`.

---

## 7. Merge-of-merges reprints the nested lattice as `T⊓T` preserve (conceptual, load-bearing)

Synthetic: M1 is introducing (`FALSE ⊓ TRUE`, tree TRUE). M2's
first parent is M1; the other parent is a topic that also has the file.
Then a non-merge `X`.

**ford** joins M1's *tree*:

```
$ ./ford exists src/app.py
FALSE     2 commits  bfa5524..6229776     A..B
FALSE     1 commit   ab6b00e              M1
       ford  FALSE ⊓ TRUE = FALSE
       origin: 3f68981  D still holds
TRUE      2 commits  7db3f0e..c0cd7a8     M2..X
       7db3f0e  M2 merge-of-merges (parent is M1)
       preserve after ford ab6b00e; not birth
       origin: 3f68981
now=TRUE  true=2/5  fords=1
```

M2 is not a ford. The join is `TRUE ⊓ TRUE` (unprinted — preserve
compresses). Occupancy of M1 never flowed.

**weir** joins M1's *occupancy*:

```
$ ./weir exists src/app.py
FALSE     1 commit   ab6b00e  M1   weir FALSE ⊓ TRUE
FALSE     1 commit   7db3f0e  M2
       weir  FALSE ⊓ TRUE = FALSE  (recursive: merge-parent contributes occupancy, not tree)
       parent ab6b00e=FALSE  occupancy  FALSE ⊓ TRUE = FALSE  (tree=TRUE)
              parent 6229776=FALSE  tree
              parent 3f68981=TRUE   tree
       parent e5a01b3=TRUE   tree
TRUE      1 commit   c0cd7a8  X non-merge
       continue after weir 7db3f0e; not birth
now=TRUE  true=1/5  weirs=2
```

Nested kizu-shaped cascade (introducing M0, then four “preserve-looking”
merges, then a non-merge tail):

| tool | TRUE span | fords/weirs |
| --- | --- | --- |
| ford | `54d914b..1a6c34e` (5 commits) `kind=preserve` after M0 | fords=1 |
| weir | `1a6c34e` (1 commit) `kind=continue` after recursive M1 | weirs=5, inherited compresses M2–M4 |

ford reprints nothing nested: one ford, then T⊓T forever. weir v2
collapses later same-origin weirs as `inherited` so the nested lattice
is printed once, not five times. CANDIDATE's suggested mutation
(“recursive join: a merge-parent that is itself a merge contributes
its occupancy, not its tree”) is weir. Already shipped. Not applied
here.

kizu §3 is this fixture at gold SHAs. PR #3–#6 (`ca0577a` `0aab861`
`0b41dc6` `ad6de10`) are ford-invisible T⊓T; weir `inherited` of
`21ae074`.

---

## What survived

- kizu `--all`: `0ea3916` is a ford, not a birth. Origin `e1098c8`.
  TRUE after it is `preserve`, not `run`. `--any` is a TRUE ford at
  the merge, not a 23-commit birth.
- Diamond `--all`: `now=FALSE`, `tree_now=TRUE`, equation `FALSE ⊓ TRUE`,
  origin is topic D. `--full --tree --list` is still the `FTFT` lie
  occupancy named.
- Timeout parent: `TRUE ⊓ UNKNOWN = UNKNOWN`, rc=3, not FALSE.
  `--timeout 0` still refused.
- Depth-1 without `--boolean`: kizu `CLAUDE.md` is SHALLOW; sitbone
  missing path is SHALLOW, not never-held.
- sitbone `FocusRiverView.swift`: first-parent `never_held=1` and hints
  `--full`; `--full` recovers **11** commits (`14b1d6e..1fefafb`);
  `git log -- PATH` is empty. Zero disagreeing merges on main — ford
  has nothing to join. Correct, not a miss.
- skills `grep preact-zero-mock` still TRUE at HEAD (47/49).
- Merge-added `F⊓F` tree=TRUE is a ford, `ford_reason=tree`.
- T⊓T preserve compresses (demo). Lattice tables still `T⊓F=FALSE`,
  `T⊔F=TRUE`, `T⊓U=UNKNOWN`, `F⊔S=SHALLOW`.
- `./demo.sh` 88/88. No rewrite of the victim.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “occupancy of a merge is a join, not a boolean on
the SHA.” kizu `0ea3916` is not held's birth. sitbone's island is not
`git log -- PATH`. Timeout is not FALSE. Depth-1 is not birth. Nothing
in this battery turned that into `git log --reverse` eras. Do not kill
because `--boolean` restores held, because TRUE *spans* `21ae074`, or
because octopus folds. Those are mutations. Killing them would throw
away the two-parent introducing join occupancy asked for.

weir is the peel: recursive occupancy at `21ae074`, `--boolean` refuse
on UNKNOWN, `--follow` refuse to berth. Already a lineage. Next
mutation of *ford* is not a second weir.

| do not kill because | mutate toward |
| --- | --- |
| kizu `0ea3916` is `FALSE ⊓ TRUE`, origin `e1098c8`; `--any` still a TRUE ford, not a 23-commit birth; sitbone `--full` island 11; timeout `⊓ UNKNOWN` is UNKNOWN rc=3; depth-1 SHALLOW; demo 88/88 | **Join inputs are parent occupancy when the parent is a merge.** kizu `21ae074` is `FALSE ⊓ TRUE`, not `T⊓T` preserve. That is weir. Do not duplicate; pipe or replace. |
| | **`--boolean` that would downcast UNKNOWN/SHALLOW/EMPTY is a refuse**, not a warning-and-do. T/F downcast of an introducing merge stays a labelled lie (`0ea3916` birth) or is dropped. Depth-1 `--boolean` must not skip the horizon (`9349dc5` silent TRUE; sitbone silent `never_held`). |
| | **`--boolean` is not a lattice downcast today.** It skips `apply_join`. If the flag remains, it should project the printed join (TRUE stay / else FALSE of *occupancy*), or it should be named `--held`. |
| | **Octopus is not two-parent.** 1-of-3 and 2-of-3 are different introductions; origin cannot be “first TRUE parent.” Majority is a different object — do not add it quietly. Display is already `A ⊓ B ⊓ C`; the hole is the inf. |
| | **`never_held` at a merge HEAD whose tree has the file is a lie of the occupancy flag.** `tree_now=TRUE` + `never_held=True` + rc=1 on diamond/octopus/merge-added. Occupancy-never is not path-never. |
| | **Rename is still path death.** `--follow` is berth; refuse it the way weir does, or do not pretend `exists old.txt` after `git mv` is this object. |
| | First-parent TRUE after an introducing merge cannot span the topic SHA (`e1098c8` is off the walk). Refusing birth at `21ae074` without rewriting the span is weir's non-merge start (`d9b9645`), not a footnote on a 22-commit preserve. |

A one-line `if boolean: refuse unless all trees in {TRUE,FALSE}` would
hide the timeout downcast and would not touch `21ae074`, octopus
arity, or `never_held` at a TRUE tree. Not applied.

Do not grow a history platform. The next mutation of this object is
*recursive occupancy at a merge-of-merges* (weir already) plus a
`--boolean` that cannot restore DESTROYER occupancy's shallow birth.
Not a prettier ford dump.
