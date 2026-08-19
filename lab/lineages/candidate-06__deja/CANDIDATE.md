# candidate-06 — deja

## Primitive

Score a git diff against the repo's own memory: this change is a RELAPSE (puts back deleted code), a RESURRECT (brings back a deleted path), or an UNDOFIX (removes a line that landed as a bugfix).

## Why this might not exist

`git log -S` only works if you already know the string. Clone detectors look at the current snapshot. Review bots do not ask "have we deleted this on purpose?" or "is this the guard from the incident commit?". The recurring annoyance is the senior-dev déjà vu: re-adding the auth bypass, dropping the empty-token check, `git checkout`ing a file that cleanup removed. There is no Unix verb for that.

Discarded as too conventional: historical file coupling (`couple`) and "which Makefile/package.json/CI script is the real one". The other non-conventional sibling was `haunt` (current-tree mentions of deleted names); deja is the sharper daily verb because it scores *this* diff.

## How to run

From this worktree:

```bash
./demo.sh
./deja --help
./deja --repo /path/to/repo
./deja --repo /path/to/repo -c HEAD
git diff OLD NEW | ./deja --repo /path/to/repo --stdin
```

Exit 0 = clean, 1 = findings, 2 = error. `--porcelain` is one TSV line per finding.

## Empirical transcript

### Fixture (before and after the improvement)

v1 and v2 both catch the designed trap. `./demo.sh` after the improvement (11/11):

```
== worktree: expect RELAPSE + UNDOFIX ==
(exit 1)
RELAPSE  high  auth.py  2  …  reintroduces-line-deleted-in-fix  fix: remove god-role auth bypass
UNDOFIX  high  parser.py 2  …  deletes-line-introduced-as-fix    fix: reject empty tokens
UNDOFIX  high  parser.py 3  …  deletes-line-introduced-as-fix    fix: reject empty tokens
ok  - worktree flags relapse and undone fix
ok  - innocent addition ignored
ok  - clean worktree is silent
ok  - stdin inverse-of-fix is a RELAPSE
ok  - unrelated feature commit is clean
ok  - human format names the relapsed identifier
ok  - moved guard is not an UNDOFIX
ok  - deleted path coming back is RESURRECT
ok  - RESURRECT clusters the file instead of per-line noise
ok  - adjective 'fixed' does not mint an UNDOFIX
ok  - resurrects unicode/space path without git-add
demo: 11 passed, 0 failed
```

v1 had no RESURRECT, no move suppression, and treated the adjective "fixed" as a bugfix (`\bfix(ed)?\b`).

### Real repos — before the improvement (v1)

Clean worktrees of kizu / sitbone / skills: silent. tenaoshi and voidtrace had dirty trees (not mutated).

`deja -c HEAD` on sitbone (`094769d Add notch-based session start/stop controls`):

```
RELAPSE  high  Sources/SitboneUI/NotchOverlay.swift:83
       reintroduces-line-deleted-in-fix
       now   .background(Circle().fill(.white.opacity(0.08)))
       then  6fb6cda5433c  Fix profile creation: one-tap auto-naming…
17 findings — VStack / padding / var body: some View / @ObservedObject / UnevenRoundedRectangle
```

`deja -c 243c46e` (kizu large-scale-refactor merge): **217** findings, mostly UNDOFIX on comments and `use crate::…` that the split *moved*.

`deja -c 04adde1` (kizu jsx/tsx): **91** findings.

voidtrace dirty tree: UNDOFIX on a `patchContentHash` sha256 line (a "fix:" commit had introduced that hash) plus RELAPSE high on `initialHealth: domain.target.resolvedHealth` because the commit subject was `feat: add fixed pellet vertical slice` — **`fixed` matched the fix regex**.

skills, invert of `46d867b remove scout.sh`: **194** per-line RELAPSE hits for one deleted file.

sitbone invert of `FocusRiverView.swift` first attempt failed (empty rev-parse); with SHA `70ec7df` v1 would have emitted ~every eligible SwiftUI line.

### Real repos — after the improvement (v2)

Same commands, same trees (read-only):

| target | v1 | v2 |
| --- | --- | --- |
| sitbone `-c HEAD` | 17 | **0** |
| kizu `-c 243c46e` (merge of the big split) | 217 | **1** |
| kizu `-c 04adde1` | 91 | **1** |
| kizu `-c bbdc37d` (split watcher) | 13 | **0** |
| voidtrace dirty worktree | many HIGH | **0** |
| tenaoshi `-c HEAD` | 3 | **0** |
| skills `-c HEAD` | 0 | **0** |
| invert sitbone `70ec7df` FocusRiverView.swift | n/a / noisy | **1 RESURRECT** |
| invert skills `46d867b` scout.sh | 194 RELAPSE | **1 RESURRECT** |

Invert of the file sitbone actually deleted:

```
$ git -C sitbone diff 70ec7df 70ec7df^ -- Sources/SitboneUI/FocusRiverView.swift \
    | ./deja --repo sitbone --stdin
RESURRECT medium Sources/SitboneUI/FocusRiverView.swift
          recreates-deleted-path (file)
          then  70ec7df64b00 2026-04-01 Clean up: remove unused FocusRiverView + SettingsWindowController
```

Invert of skills' deleted scout:

```
RESURRECT medium codebase-investigator/scripts/scout.sh
          recreates-deleted-path (file)
          then  46d867b11d8e 2026-03-12 remove scout.sh and redesign Phase 1 to use Claude native tools
```

Remaining v2 hits that look like leftover noise (not silenced; recorded):

```
kizu 243c46e  RELAPSE medium  src/ui/diff_view.rs:11
  diff_line::{render_diff_line, render_diff_line_wrapped},
  (use-tree fragment, not a file-level resurrection)

kizu 04adde1  RELAPSE medium  src/hook/tests.rs:189
  let hits = scan_scars(std::slice::from_ref(&file));
  (test helper line reused after the hook.rs split)
```

Ugly fixture (spaces + `バックドア.py`), untracked, no `git add`:

```
RESURRECT high  old copies/v1/バックドア.py
          recreates-deleted-path
          then  fix: delete leftover backdoor helper
```

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (244 commits; large-split merge)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (FocusRiverView deletion)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (dirty generated/scenario tree, not mutated)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (dirty + HEAD)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (deleted scout.sh / circuit-breaker)
- Synthetic fixture in `./demo.sh` (auth bypass, empty-token guard, file move, unicode path)

`stratal` was an empty directory, not a git repo.

## Surprises

- Conventional-commit `fix:` is not the same as the English word `fixed`. Game/engine repos say "fixed pellet", "fixed-width" and v1 treated those as incident commits.
- Reviewing a merge against `--no-merges` history matches the merge's *own* split commits (delete from `app.rs`, add to `app/picker.rs`). Must exclude `rev-list commit^..commit`.
- A "deleted file" in the working tree is usually *untracked*, so `git diff HEAD` is blind to the most literal resurrection. Default `--untracked=resurrect` exists because of that.
- Git C-quotes `old copies/v1/バックドア.py` as `"old copies/v1/\343\203\220…"`. Without `core.quotepath=false` plus an unquoter, resurrection never fires on the paths that most need it.
- `.expect("…")` is a guard, so moving a test helper that contains `expect` looks like UNDOFIX until move detection uses identifier Jaccard, not exact lines.

## Failures

- v1 sitbone HEAD: 17 SwiftUI boilerplate "relapses".
- v1 kizu merge: 217 moved comments/imports flagged as UNDOFIX.
- v1 voidtrace: `fixed pellet` and sha256 hashes.
- v1 skills scout invert: 194 lines instead of one file finding.
- First sitbone invert in the shell used an empty SHA (`git log --diff-filter=D -- path` returned nothing in that invocation).
- Untracked new files that are *not* historical deletions are still invisible unless `--untracked=all`.
- Two medium leftovers on kizu remain (use-tree fragment; reused test line).
- No symbol parser: a reformatted relapse with no shared rare identifiers is a miss.
- `--untracked=all` on a huge untracked tree was not fully characterized.

## Suggested mutations

- `deja --haunt`: current-tree mentions of *deleted identifiers*, not just of this diff (the sibling primitive).
- Oscillation / `regret`: names deleted and re-added more than once.
- Language-aware function bodies (tree-sitter) so a moved-and-renamed guard still matches.
- Pre-commit mode that only fails on `high`.
- Ignore generated/oracle paths via a repo `.dejaignore`.
- Attribute a RELAPSE to the deleting commit's test file ("the test that justified the deletion").

## Kill / keep

**Keep.** The verb is new, the Unix shape is small (`diff in → findings out → exit 1`), and dogfood on kizu/sitbone/skills produced real before/after numbers, not a toy-only story. Kill only if a later generation proves that `git log -S` plus a three-line wrapper gets the same precision — v1 showed that the naive version does not.
