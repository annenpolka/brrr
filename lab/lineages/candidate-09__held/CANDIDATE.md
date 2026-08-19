# candidate-09 — held

## Primitive

`held` emits the contiguous eras of git history where an arbitrary predicate is true.

Bisect finds **one** transition and assumes monotonicity. `git log -S` finds commits that **changed** a string. `held` answers a different question: *during which intervals was this true?*

Observers: `exists PATH`, `grep PATTERN`, `exec -- CMD`. Output is eras (human / `--oneline` / `--json` / `--revs` / `--bounds`). Exit 0 iff the predicate holds at the last sample.

## Why this might not exist

`git log -- PATH` **lies** for deleted files (history simplification): sitbone's `FocusRiverView.swift` produces an empty log even though it was added and deleted. `git bisect` cannot report a birth-death-rebirth. There is no Unix verb whose value is an occupancy interval.

Discarded as too conventional: `aged` (grep|blame age) and `culprit` (delta-debug dirty hunks). The other unusual primitive, `haunt` (death certificate + living DNA of a deleted path), is a suggested mutation.

## How to run

```bash
./held --help
./demo.sh
./held -C /path/to/repo exists some/path
./held -C /path/to/repo --full grep FocusRiverView
./held -C /path/to/repo --now exists dirty.txt
```

## Empirical transcript

### Before the improvement (commit 30fd643)

Synthetic fixture (oscillating path, rename with spaces, Japanese filename, nested git) already passed: `oscillate.txt` eras `TFTF`, `TOKEN_A` reincarnated from `keep.txt` to `other.txt`, `exec` saw the two-line window of `keep.txt`.

Real repos:

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# (empty)  — the footgun

$ ./held -C sitbone exists Sources/SitboneUI/FocusRiverView.swift
# exists Sources/SitboneUI/FocusRiverView.swift  (sitbone, 31 commits, first-parent)
FALSE  31 commits  a2512fe..094769d  2026-03-31 → 2026-04-17
hint: never held on first-parent, but existed in 11 reachable commits off the mainline
      (14b1d6e..1fefafb  2026-03-31 → 2026-04-01). rerun with --full

$ ./held -C sitbone --full exists Sources/SitboneUI/FocusRiverView.swift
FALSE  11 commits  a2512fe..74363dc
TRUE   11 commits  14b1d6e..1fefafb  2026-03-31 → 2026-04-01
FALSE  78 commits  70ec7df..094769d
now=FALSE  true=11/100

$ ./held -C skills exists circuit-breaker/scripts/detect.sh
FALSE  15 commits  9adb747..5317362
TRUE    6 commits  11716a3..e0ad330  2026-04-07
FALSE  28 commits  2d56b11..6b19433
```

**v1 failures on real queries:**

```
$ ./held -C voidtrace grep finite breakpoint
# grep finite -- breakpoint   (voidtrace, 78 commits, first-parent)
FALSE  78 commits  ae29226..ce44c93
now=FALSE  true=0/78
# silent! "breakpoint" was eaten as a pathspec that never existed.

$ ./held -C voidtrace grep 'finite breakpoint'
FALSE  78 commits
# still silent: blobs say "finite Breakpoint", not "finite breakpoint".

$ ./held -C sitbone grep FocusRiverView
FALSE  31 commits
# no --full hint (exists had one; grep did not).

$ ./held -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 commits, first-parent)
# 24 first-parent commits vs 244 reachable — compression invisible.
```

### After the improvement

Same commands:

```
$ ./held -C voidtrace grep finite breakpoint
# grep finite -- breakpoint  (voidtrace, 78 commits, first-parent)
FALSE  78 commits  ae29226..ce44c93
warning: pathspec 'breakpoint' matched no file in any scanned commit.
         If you meant a phrase, quote it: held grep 'finite breakpoint'

$ ./held -C voidtrace grep 'finite breakpoint'
FALSE  78 commits
hint: 0 case-sensitive matches; 3 commits match with -i
      (e.g. .agents/skills/voidtrace/SKILL.md). rerun with -i

$ ./held -C voidtrace grep -i 'finite breakpoint'
FALSE  75 commits  ae29226..66d6fa1  2026-07-29 → 2026-08-01
TRUE    3 commits  6e3368b..ce44c93  2026-08-02
       witnesses: .agents/skills/voidtrace/SKILL.md,
                  .agents/skills/voidtrace/scripts/run-breakpoint.ts, ...
now=TRUE  true=3/78

$ ./held -C sitbone grep FocusRiverView
# grep FocusRiverView  (sitbone, 31 of 100 commits, first-parent)
FALSE  31 commits
hint: never held on first-parent, but matched in 11 reachable commits
      off the mainline (14b1d6e..1fefafb). rerun with --full

$ ./held -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 of 244 commits, first-parent)
```

`--full` on kizu then names the real birth (`e1098c8 chore: bootstrap CLAUDE.md...`) instead of the merge that first-parent reports.

Other dogfood that just worked:

```
$ ./held -C tenaoshi grep '第一級'
FALSE  16 commits  a41089c..4878b75
TRUE    2 commits  70b450d..3798ea7
       witnesses: AGENTS.md, docs/SPEC.md, specs/tenaoshi.pkl
# the commit that changed prompt.md's role is exactly the era start.

$ ./held -C skills exists preact-zero-mock/SKILL.md
FALSE  2 / TRUE 31 / FALSE 16   (born 2026-03-06, died 2026-05-09)

$ ./held -C stratal exists README.md
held: no commits at HEAD (empty repository?)   # exit 2, no stacktrace
```

`./demo.sh` — 33 assertions, exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (100 commits; deleted `FocusRiverView.swift` invisible to `git log -- path`)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (circuit-breaker, preact-zero-mock life/death)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (24 first-parent / 244 full; CLAUDE.md, `line_number`)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (phrase + case footguns)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (Japanese predicate `第一級`)
- `/Users/annenpolka/ghq/github.com/annenpolka/stratal` (empty repo)
- synthetic fixture in `demo.sh`: oscillating path, rename with spaces, `計画.md`, nested git, `--now` dirty resurrection

## Surprises

- GitHub-flow first-parent is tiny (kizu 24 vs 244). Occupancy on mainline is the merge, not the feature commit.
- A file can be an ancestor of HEAD and still **never** exist on first-parent trees: sitbone added and deleted `FocusRiverView.swift` on a side branch that merged after the file was already gone. `git log -- PATH` then prints nothing.
- `git grep` of a two-word phrase is case-sensitive on the second word (`finite Breakpoint`) — humans do not type that.
- Rename is a path death. That is correct for `exists` (path identity) and surprising if you wanted content lineage.

## Failures

- v1 silently treated `held grep finite breakpoint` as `grep finite -- breakpoint` (never held).
- v1 silently missed `finite Breakpoint` when asked for `finite breakpoint`.
- v1 grep lacked the `--full` hint that exists already had.
- v1 hid first-parent compression (24 vs 244).
- `exists` does not follow renames (documented, not yet a flag).
- `exec` is a real checkout in a throwaway worktree; fine for these repos, not for multi-minute test suites.
- Full-history eras are ordered by `git log --reverse`, not a merge-diamond lattice. Adjacent in the list is not always adjacent in time.

## Suggested mutations

- `haunt PATH` — death certificate + living files that still share unique lines with the ghost.
- `--follow` / `exists --identity` so a rename is one era, not a death and a birth.
- Split grep eras when the **witness set** changes, not only the boolean (TOKEN_A moving from `keep.txt` to `other.txt` is one TRUE era today).
- `held count PATTERN` — integer time series, not boolean.
- Stash / other worktrees as extra samples beside `--now` / `--index`.
- Cache probe results in `.git/held-cache/` keyed by `(sha, predicate)`.

## Kill / keep

**Keep.** It is a small verb, it is not a wrapper, and on the first real deleted file it beat `git log -- path`. The v1→v2 change was forced by real queries, not polish.
