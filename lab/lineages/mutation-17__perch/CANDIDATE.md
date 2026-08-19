# mutation-17 — perch

## Primitive

`perch` emits occupancy eras that also split when the **witness set** changes. Same TRUE, different files (or lines) holding it → a new era. Occupancy + who is holding.

Ancestor `held` compresses a boolean. `perch --boolean` is that ancestor. Default `perch` is tenure.

## Why this might not exist

`git log -S` finds commits that *changed* a string. `git bisect` finds one cut. `held` finds intervals where a predicate is true — and then treats every TRUE sample as the same era, even when the name moved from `keep.txt` to `other.txt`, or a plugin died and only README still says the word.

There is no Unix verb whose value is **who is currently holding a still-true fact**. Blame is line identity. Log is change events. Occupancy without a holder is how `grep preact-zero-mock` says TRUE sixteen commits after the plugin was deleted.

Discarded as too conventional: wrapping `git log --name-only -S`, plotting a file-count time series, blaming the first holder.

## How to run

```bash
./perch --help
./demo.sh
./perch -C /path/to/repo grep TOKEN_B
./perch -C /path/to/repo --boolean grep TOKEN_B
./perch -C /path/to/repo --grain loci grep TOKEN_B
./perch -C /path/to/repo --full grep FocusRiverView
./perch -C /path/to/repo grep preact-zero-mock
```

## Empirical transcript

### Before the improvement (commit a19f99e)

Synthetic fixture already split TOKEN_B copy-then-move (`alpha.txt` → `alpha.txt,beta.txt` → `beta.txt`) while occupancy never flipped: `boolean=1`, `eras=3`. `--boolean` recovered one TRUE era. `--grain lines` split the t3 line-number shift (4 eras); `--grain loci` did not.

Real repos — holder splits worked, ghost occupancy was silent:

```
$ ./perch -C sitbone --full grep FocusRiverView
FALSE  11 commits
TRUE    1 commit   holders: FocusRiverView.swift
TRUE    5 commits  holders: FocusRiverView.swift, NotchOverlay.swift
       + NotchOverlay.swift
TRUE    5 commits  holders: FocusRiverView.swift
       - NotchOverlay.swift
FALSE  78 commits
now=FALSE  true=11/100  eras=5  boolean=3  holder_splits=2

$ ./perch -C sitbone --full --boolean grep FocusRiverView
FALSE / TRUE 11 / FALSE          # ancestor held: one island, witnesses the .swift file

$ ./perch -C skills grep preact-zero-mock
FALSE   2 commits
TRUE   21 commits  holders: preact-zero-mock/SKILL.md
TRUE   10 commits  holders: README.md, preact-zero-mock/SKILL.md
       + README.md
TRUE   16 commits  holders: README.md
       - preact-zero-mock/SKILL.md
now=TRUE  true=47/49  eras=4  boolean=2  holder_splits=2
# silent! last sixteen commits are a mention in README after 127df9c deleted the plugin.

$ ./perch -C skills --boolean grep preact-zero-mock
FALSE  2 / TRUE 47
now=TRUE
       witnesses: preact-zero-mock/SKILL.md
# held's answer. The definition is the start of a 47-commit TRUE run.
# HEAD does not have that file.
```

v1 already beat `git log -- Sources/SitboneUI/FocusRiverView.swift` (empty) the way held did, and further split the island when NotchOverlay started and stopped naming the type. The miss was skills: occupancy continued, the holder became documentation, and v1 did not say so.

### After the improvement

Same `grep preact-zero-mock` command:

```
$ ./perch -C skills grep preact-zero-mock
FALSE   2 commits
TRUE   21 commits  holders: preact-zero-mock/SKILL.md
TRUE   10 commits  holders: README.md, preact-zero-mock/SKILL.md
       + README.md
TRUE   16 commits  holders: README.md
       - preact-zero-mock/SKILL.md
       ghost: definition left; name still perches in documentation
now=TRUE  true=47/49  eras=4  boolean=2  holder_splits=2
hint: now=TRUE only as a documentation mention (README.md); definition preact-zero-mock/SKILL.md is gone
```

Contrast that is *not* a ghost — remaining holder is still code:

```
$ ./perch -C sitbone --full grep FocusRiverView
# last TRUE era drops NotchOverlay.swift, keeps FocusRiverView.swift
# kind=shrink, not ghost. The type still lives in its file. Then boolean death.
```

`grep debug-mode` on skills is always TRUE from commit 0 (boolean=1) with three tenures: definition → cited by constraint-as-output → README catalog. SKILL.md still holds, so no ghost. `exists circuit-breaker/scripts/detect.sh` is a clean FTF path death — exact exists has a one-file holder, same answer as held.

`exists '*SKILL.md'` is always TRUE (boolean=1) and 23 holder eras: a changelog of the catalog. Occupancy of "there is a skill" is one interval; who is holding the glob is the inventory.

```
$ ./perch -C tenaoshi grep '第一級'
FALSE  16 / TRUE 2
       holders: AGENTS.md, docs/SPEC.md, specs/tenaoshi.pkl
# no holder split; the policy word arrived in three files at once. Same as held.
```

`./demo.sh` — 57 assertions, exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView island `git log -- path` cannot see; NotchOverlay gained then lost the name while the file lived
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — `preact-zero-mock` ghost occupancy; `debug-mode` holder growth; `circuit-breaker` boolean death; glob `*SKILL.md` catalog
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — Japanese predicate `第一級` (no holder split)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — first-parent compression; `line_number` spreads across plans/docs
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — phrase + case footguns kept from held
- synthetic fixture: TOKEN_B copy/move with no FALSE gap; TOKEN_A reincarnation; line-number shift vs loci grain; `--now`; nested git; empty repo

## Surprises

- The interesting split is not TOKEN_A (FALSE already cuts it). It is TOKEN_B / preact-zero-mock: occupancy never dies and the holder does.
- `grep` of a deleted plugin is a *worse* liar than `exists`. `exists preact-zero-mock/SKILL.md` is FALSE after 127df9c. `grep preact-zero-mock` is TRUE at HEAD. held reports that TRUE as one 47-commit era whose witnesses start at the definition. perch's last era is README only.
- Dropping a *code* holder is not a ghost. FocusRiverView losing NotchOverlay is shrink; the type still perches in its file. Ghost is: remaining holders are documentation, a non-doc holder left.
- Glob `exists '*SKILL.md'` turns a single TRUE occupancy into the plugin inventory. That is correct for "who is holding" and loud if you wanted "did any skill exist".
- `--grain lines` splits when someone inserts a header above a match. `--grain loci` (path + line text) ignores that. Default grain is files; lines are opt-in because they are noisy.
- kizu `grep line_number` on first-parent is 2 boolean eras and 8 holder eras, mostly plans/ spreading. A living identifier accretes docs. That is the SiteObserver problem too.

## Failures

- v1 split holders but did not name ghost occupancy. skills `now=TRUE` looked like the plugin still existed.
- `--boolean` v1 printed only the *start* witnesses of a long TRUE run (`SKILL.md`), hiding that HEAD's holder was README.md. Fixed to union start+end, matching held.
- `exists` of an exact path cannot split on holders (the holder *is* the path). Rename is still a death. Same as held; `--follow` is a different mutation.
- Full-history eras are still ordered by `git log --reverse`, not a merge-diamond lattice. Adjacent in the list is not always adjacent in time.
- `exec` holders are stdout lines. A noisy command fragments eras. Silent predicates (`test -f`) stay boolean.
- Glob catalog walks (`*SKILL.md`) emit one era per addition. No `--min-era` / `--ignore docs` yet.
- `is_doc_holder` is a basename heuristic (README, docs/, AGENTS.md, …). A definition that *is* a markdown SKILL.md is code for this purpose, which is why preact-zero-mock's ghost fires on SKILL.md leaving and README remaining.
- `git grep` of unquoted two-word phrases is still a pathspec. Warning kept from held, program name updated.

## Suggested mutations

- `--follow` so a rename is one perch, not a path death plus a birth.
- `perch count PATTERN` — integer occupancy per sample, not boolean+set.
- Ignore-docs / `--code` grain so kizu `line_number` and sitbone SiteObserver do not fragment on ADR accretion.
- Pipe from `tell`: `tell A B | perch --range A..main` walks the predicate just found, then splits on who holds it.
- Cache probes in `.git/perch-cache/` keyed by `(sha, predicate, grain)`.
- Stash / other worktrees as extra samples beside `--now` / `--index`.

## Flipped assumption: bought and lost

Ancestor `held` assumed **TRUE is TRUE**. One occupancy interval, witnesses as a footnote. The suggested mutation on held was this file: split when the witness set changes.

**Bought**

- Copy and move without a FALSE gap become visible (TOKEN_B; FocusRiverView ↔ NotchOverlay).
- `grep` that stays true after a deletion is no longer a 47-commit blob. The last tenure is named, and if it is documentation-only, it is a ghost.
- `--boolean` is an explicit downcast to held, not a fork of the probe machinery.
- Grain is a knob: files / loci / lines. Line-number drift is not the default split.

**Lost**

- Eras are no longer a pure boolean occupancy. TFTF diagrams lie; `boolean=2 holder_splits=2` is the real shape.
- Growing modules fragment (kizu `line_number`, glob `*SKILL.md`). held's one TRUE era was more readable there.
- "Who is holding" for `exists PATH` is PATH. The interesting splits are grep/glob.
- Ghost is a heuristic over remaining holders, not a proof the definition is dead (`exists` already answers that). It is a warning on the grep lie.
- Two snapshots still need `tell`. perch does not invent the predicate.

## Kill / keep

**Keep.** It is a small verb, it is not a wrapper, and on the first real deleted plugin it showed that `grep` occupancy can outlive the thing you thought you were asking about. The v1→v2 change was forced by skills `preact-zero-mock`, not polish.
