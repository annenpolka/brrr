# reimpl-02 — dwelt

## Primitive

`dwelt` emits the contiguous eras of git history where an arbitrary predicate is true.

Reimplementation of `held` under a new name, from observed CLI behavior only (README, `demo.sh`, `--help`, and live runs — not the `held` source). Same question: *during which intervals was this true?* — not one bisect cut.

Observers: `exists PATH`, `grep PATTERN`, `exec -- CMD`. Output is eras (human / `--oneline` / `--json` / `--revs` / `--bounds`). Exit 0 iff the predicate holds at the last sample.

## Why this might not exist

`git log -- PATH` **lies** for deleted files (history simplification): sitbone's `FocusRiverView.swift` produces an empty log even though it was added and deleted. `git bisect` cannot report a birth-death-rebirth. Occupancy intervals are a missing Unix verb. Rebuilding from the outside tests whether the primitive is real or an accident of one implementation.

## How to run

```bash
./dwelt --help
./demo.sh
./dwelt -C /path/to/repo exists some/path
./dwelt -C /path/to/repo --full grep FocusRiverView
./dwelt -C /path/to/repo --now exists dirty.txt
```

## Empirical transcript

### Before the improvement

Synthetic fixture (oscillating path, rename with spaces, Japanese filename, nested git) matched `held`: `oscillate.txt` eras `TFTF`, `TOKEN_A` reincarnated from `keep.txt` to `other.txt`, `exec` saw the two-line window of `keep.txt`.

Real-repo comparison against original `held` (JSON era pattern, counts, start/end shorts):

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# (empty)  — the footgun

$ ./dwelt -C sitbone exists Sources/SitboneUI/FocusRiverView.swift
# exists Sources/SitboneUI/FocusRiverView.swift  (sitbone, 31 of 100 commits, first-parent)
FALSE  31 commits  a2512fe..094769d  2026-03-31 → 2026-04-17
hint: never held on first-parent, but existed in 11 reachable commits off the mainline
      (14b1d6e..1fefafb  2026-03-31 → 2026-04-01). rerun with --full

$ ./dwelt -C sitbone --full exists Sources/SitboneUI/FocusRiverView.swift
FALSE  11 commits  a2512fe..74363dc  2026-03-31
TRUE   11 commits  14b1d6e..1fefafb  2026-03-31 → 2026-04-01
FALSE  78 commits  70ec7df..094769d  2026-04-01 → 2026-04-17
now=FALSE  true=11/100

$ ./dwelt -C skills exists circuit-breaker/scripts/detect.sh
FALSE  15 commits  9adb747..5317362  2025-12-19 → 2026-04-07
TRUE    6 commits  11716a3..e0ad330  2026-04-07
FALSE  28 commits  2d56b11..6b19433  2026-04-07 → 2026-07-25
```

JSON bounds matched `held` exactly on sitbone first-parent, sitbone `--full`, and skills circuit-breaker.

**v1 gap on kizu (first-parent occupancy starts at a merge):**

```
$ ./dwelt -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 of 244 commits, first-parent)
FALSE   1 commit   cbaf29a  2026-04-15
TRUE   23 commits  0ea3916..9349dc5  2026-04-15 → 2026-05-04
       0ea3916  Merge pull request #1 from annenpolka/chore/bootstrap-ci-and-claude-md
now=TRUE  true=23/24

$ ./dwelt -C kizu --full exists CLAUDE.md
TRUE  243 commits  e1098c8..9349dc5
       e1098c8  chore: bootstrap CLAUDE.md, CI, and t-wada TDD conventions
```

First-parent names the merge. The file was born on the topic branch at `e1098c8`. `held` had the same blind spot: it hinted `--full` only when the predicate *never* held on first-parent, not when it held starting at a merge.

### After the improvement

Same sitbone/skills commands still match `held` exactly (origin only attaches when a first-parent TRUE era *starts at a merge*).

```
$ ./dwelt -C kizu exists CLAUDE.md
# exists CLAUDE.md  (kizu, 24 of 244 commits, first-parent)
FALSE   1 commit   cbaf29a  2026-04-15
TRUE   23 commits  0ea3916..9349dc5  2026-04-15 → 2026-05-04
       0ea3916  Merge pull request #1 from annenpolka/chore/bootstrap-ci-and-claude-md
       9349dc5  release: v0.7.0
       origin: e1098c8  chore: bootstrap CLAUDE.md, CI, and t-wada TDD conventions
                      (1 commit before this merge)
now=TRUE  true=23/24
```

First-parent still answers the mainline question (occupancy begins at the merge). The origin line names the real birth `held` only showed under `--full`. A synthetic `--no-ff` fixture in `demo.sh` asserts the same: era start is the merge, `origin.short` is the topic birth.

`./demo.sh` — 39 assertions, exit 0, including era match vs `held` on sitbone (first-parent and `--full`) and skills circuit-breaker.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (100 commits; deleted `FocusRiverView.swift` invisible to `git log -- path`)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (circuit-breaker life/death)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (24 first-parent / 244 full; CLAUDE.md born behind a merge)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (phrase + case footguns)
- synthetic fixture in `demo.sh`: oscillating path, rename with spaces, `計画.md`, nested git, `--now` dirty resurrection

## Surprises

- GitHub-flow first-parent is tiny (kizu 24 vs 244). Occupancy on mainline is the merge, not the feature commit.
- A file can be an ancestor of HEAD and still **never** exist on first-parent trees (sitbone `FocusRiverView.swift`).
- `git ls-tree COMMIT -- 'glob'` does not glob; `git ls-files --with-tree=COMMIT` does. Observed only because the fixture used `nested/deep/*`.
- Rename is a path death. Correct for `exists` (path identity).

## Failures

- `exists` does not follow renames (same as `held`).
- `exec` is a real checkout in a throwaway worktree.
- Full-history eras are ordered by `git log --reverse`, not a merge-diamond lattice.

## Suggested mutations

- `--follow` / `exists --identity` so a rename is one era.
- Split grep eras when the **witness set** changes.
- `dwelt count PATTERN` — integer time series, not boolean.

## Kill / keep

**Keep.** Rebuilt from the outside, it reproduced `held`'s sitbone/skills answers exactly. The first improvement was forced by kizu: first-parent occupancy starts at a merge, so v1 (like `held`) named the merge and hid `e1098c8`. The primitive survived a clean-room reimplementation and then beat its ancestor on that merge-birth case.
