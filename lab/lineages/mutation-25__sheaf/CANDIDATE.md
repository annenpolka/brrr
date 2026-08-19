# mutation-25 — sheaf

## Primitive

`sheaf` takes two git trees and emits the **shortest covering set** of predicates that together distinguish them, printed as ready-to-run `held` / `perch` command lines.

Ancestor `tell` lists unary predicates (optional `--cover`). `sheaf`'s value is the set plus the walks. Two trees in; paste a line into the shell.

## Why this might not exist

`tell A B` answers "what questions split these trees?" Then you retype the interesting one into `held` or `perch`. The heretic asked for `tell A B | perch --range`. Diff is a file list. Tell is a catalog. Held/perch assume you already know the predicate. There is no Unix verb whose value is the shortest *set* of questions that cover a delta *and* the commands that occupy them.

Discarded as too conventional: defaulting `tell --cover`, wrapping `git diff --name-status`, echoing `held …` after the catalog.

## How to run

```bash
./sheaf --help
./demo.sh
./sheaf -C /path/to/repo HEAD~1 HEAD
./sheaf -C /path/to/repo --walks 14b1d6e HEAD
./sheaf -C /path/to/repo --held --kind exists,grep 14b1d6e HEAD
./sheaf HEAD :worktree
```

## Empirical transcript

### Before the improvement

v1 used tell's global occupancy greedy as the sheaf, then printed walks. Adjacent births looked right. Island-vs-HEAD did not.

```
$ ./sheaf -C sitbone --limit 8 14b1d6e HEAD
sheaf
  B  17  grep SiteObserver           17 files
  B  18  grep SensorReading           8 files
  B  12  grep Logging                 7 files
  B  16  grep -F pre-push             4 files
  B  19  grep SessionProfile          7 files
  B  22  grep WindowTitleParser       7 files
  B  24  grep CameraFrameProvider     9 files
  B  25  exists *JSONSessionStore*    2 files
unexplained  … Sources/SitboneUI/FocusRiverView.swift …
# the island's unique name is unexplained. git log -- PATH is empty.
# that is tell --cover's occupancy trap, now the *product*.
```

Ancestor `tell --cover --limit 6` on the same pair is the same B-side module index; FocusRiverView never enters the set under a size cap.

### After the improvement

Exclusive sides are reserved a slot. `--limit` is the total size. Lockfiles drop out of the covering universe. Content-line greps rank last.

```
$ ./sheaf -C sitbone --limit 6 14b1d6e HEAD
sheaf
  A  19  grep FocusRiverView          1 file
  B  17  grep SiteObserver           17 files
  B  24  grep CameraFrameProvider     9 files
  B  12  grep Logging                 7 files
  B  18  grep SensorReading           8 files
  B  19  grep SessionProfile          7 files

walk
  held  -C sitbone --full --rev 094769d grep FocusRiverView
  perch -C sitbone --full --rev 094769d grep FocusRiverView
  held  -C sitbone --full --rev 094769d grep SiteObserver
  perch -C sitbone --full --rev 094769d grep SiteObserver
  …
```

Paste the first perch line (binary from mutation-17):

```
$ perch -C sitbone --full --rev 094769d grep FocusRiverView
FALSE  11 commits  a2512fe..74363dc
TRUE    1 commit   holders: FocusRiverView.swift
TRUE    5 commits  holders: FocusRiverView.swift, NotchOverlay.swift
       + NotchOverlay.swift
TRUE    5 commits  holders: FocusRiverView.swift
       - NotchOverlay.swift
FALSE  78 commits  70ec7df..094769d
```

`git log -- Sources/SitboneUI/FocusRiverView.swift` is empty. The sheaf named the predicate and the `--full` flag held's sitbone hint used to make you type.

Birth (parent-child) does not need `--full`; the walk is cheap:

```
$ ./sheaf -C sitbone 14b1d6e^ 14b1d6e
sheaf
  B  19  grep FocusRiverView          1 file
  B  15  grep onSettings              2 files
walk
  held  -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
  perch -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
  …

$ held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
FALSE  11 commits  a2512fe..74363dc
TRUE    1 commit   14b1d6e
       witnesses: Sources/SitboneUI/FocusRiverView.swift
now=TRUE  true=1/12
```

Death certificate, opposite side, same predicate:

```
$ ./sheaf -C sitbone 70ec7df^ 70ec7df
sheaf
  A  19  grep FocusRiverView
  A  13  grep settings
walk
  held -C sitbone --rev 70ec7df --limit 12 grep FocusRiverView

$ held -C sitbone --rev 70ec7df --limit 12 grep FocusRiverView
TRUE   11 commits  14b1d6e..1fefafb
FALSE   1 commit   70ec7df
now=FALSE  true=11/12
```

kizu CLAUDE.md birth — three exclusive facts, three walks:

```
$ ./sheaf -C kizu e1098c8^ e1098c8
sheaf
  B  15  exists *CLAUDE*
  B  12  exists *.yml
  B  13  grep awaiting
walk
  held -C kizu --rev e1098c8 --limit 12 exists *CLAUDE*
  …

$ held -C kizu --rev e1098c8 --limit 12 exists *CLAUDE*
FALSE  1 commit   cbaf29a
TRUE   1 commit   e1098c8
       witnesses: CLAUDE.md
```

kizu jsx/tsx (`04adde1`): sheaf leads with `exists *jsx-tsx.test*`, `exists *0020-tree-sitter-for-jsx-tsx*`, `grep js_ts`. `exists *language*` is a short glob that covers `src/language.rs` + `js_ts.rs` — shortest, not the most characteristic.

`./demo.sh` — 20 assertions, exit 0. Generated fixture `held` line actually ran.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView birth, death, island-vs-HEAD (`git log -- path` empty); generated `held`/`perch --full` lines executed
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — CLAUDE.md + CI birth; jsx/tsx feature commit
- synthetic fixture in `demo.sh`: oscillating path, rename with spaces, `計画.md`, nested git, `:worktree` dirty resurrection, empty repo

## Surprises

- Shortest *set* is not shortest *predicate*. `grep oscillate` (14) beat `exists *oscillate*` (19) on a one-file death. Both split the trees; the set has size 1. Exists is the occupancy question a human types; length-min picked grep.
- A global occupancy cover *is* tell `--cover`. Making it the product made the island failure unmissable: FocusRiverView became unexplained instead of merely ranked 80th.
- `--full` is not a style flag. Island vs HEAD is off first-parent; birth vs parent is not. Wrong default and you re-learn held's sitbone hint. Ancestry of the true-side commit against `--rev` is enough to pick it.
- Exclusive-side reservation of 1–2 slots is enough. Island `--limit 6` is `FocusRiverView` + five HEAD module names. The lockfile `.claude/scheduled_tasks.lock` is the other only-A path; dropping skip-token paths from the universe removed it without hiding FRV.
- Generated perch on the island is the heretic's `tell × perch` in one paste: boolean occupancy plus NotchOverlay joining and leaving the holder set.
- kizu's shortest exclusive glob is `exists *language*` (2 files) and `exists *.yml` (first yaml). Characteristic and shortest still disagree; we keep both kinds.

## Failures

- v1 global greedy + `--limit` dropped FocusRiverView from the sheaf on the 72-path island.
- v1 per-side limit-without-total-cap emitted 14 predicates including `grep scheduled_tasks`, `grep -F 'に集約'`, and a 133-character test line. Shortest set it was not.
- `grep settings` on the death commit is a leftover word from SitboneApp.swift. The sheaf already has FocusRiverView; the second member is the other changed path's shortest token, not a second story.
- kizu jsx sheaf still grows fixture filenames (`*jsx-tsx-complete-support*`, `*0020-tree-sitter-for-jsx-tsx*`). Glob compression of `*jsx-tsx*` is incomplete; `grep js_ts` is the token you would actually walk.
- `exists *language*` is shorter than `exists *js_ts*` and covers two files. Shortest set wins; the walk is a worse question.
- Walk lines name `held`/`perch` on PATH. Demo rewrites the token to a worktree binary. A machine without them still gets a pasteable line that will fail.
- Binary-only modifies have no unary grep; they remain unexplained except by "blob differs", which is not a held predicate.
- Far-apart trees still leave an unexplained tail (island +29 paths). `--limit` is the point; the tail is lockfiles, workflows, AGENTS.md.
- Full-tree token uniqueness loads both blobs. Fine for sitbone/kizu, not argued for a monorepo.

## Suggested mutations

- Pipe the sheaf into held/perch (`sheaf A B | perch --stdin`) so the walk is not copy-paste.
- Prefer `exists` over `grep` when both cover the same exclusive singleton (oscillate.txt, CLAUDE.md).
- Collapse fixture-filename exists (`*jsx-tsx.test*` / `*0020-tree-sitter-*`) into one glob `*jsx-tsx*`.
- `--follow` so a rename is one identity.
- Cache first-parent lists in `.git/sheaf-cache/`.

## Flipped assumption: bought and lost

Ancestor `tell` assumed **the user wants a ranked list of independent predicates**.

**Bought**

- The output is a set that covers the delta. You do not re-rank a catalog.
- Each member is already a `held` / `perch` command line. Reverse-and-forward is one paste. Off-first-parent islands emit `--full`.
- Exclusive-side reservation keeps the island's unique name under a size budget that occupancy-greedy spends on HEAD.

**Lost**

- The catalog is hidden unless `--predicates`. Some true predicates never print.
- Time is still held's job; sheaf only names the walks.
- Two snapshots, not a three-state occupancy interval (`TOKEN_A` in keep.txt then other.txt is two pairwise sheaves).
- "Shortest set" will pick `exists *language*` over `grep js_ts` when the glob is shorter and covers more exclusive files. Characteristic and shortest still fight.

## Kill / keep

**Keep.** It is not `tell --cover` with extra echo. On the first real deleted-file island it emitted `perch --full grep FocusRiverView`, which ran and split NotchOverlay holders, without being told the name or `--full`. The v1→v2 change was forced by sitbone island output, not polish.
