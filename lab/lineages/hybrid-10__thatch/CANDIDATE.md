# hybrid-10 — thatch

## Primitive

Two git trees in. Emit the **shortest covering set of path-conditions** that distinguish them, then **occupy those stacks through history**.

A file move is one stack whose holders changed. Not sheaf's grep/exists. Not a user-pinned `tenure FILE:LINE`.

## Why this might not exist

`sheaf A B` answers "which unary predicates cover this delta?" and prints `held`/`perch` walks. `tenure FILE:LINE` answers "when did *this* stack hold, and who sat in it?" Developers who have both still have two reports: a catalog of greps, then a pin they have to invent.

`sheaf | tenure` greps the if-text. The if-text lives on the guard. Occupancy of a path-condition is the lines that run under the stack. Sheaf cannot emit `git.rs → parse.rs` as one member. Tenure cannot invent the stack from two trees, and cannot occupy a pin whose file is gone at `--rev`.

Discarded as concatenation: wrapping sheaf then tenure; covering with `exists *parse.rs*` and occupying the first witness line; printing two sections.

## How to run

```bash
chmod +x ./thatch
./thatch --selftest
./demo.sh
./thatch -C /Users/annenpolka/ghq/github.com/annenpolka/kizu 3b3e0a9^ 3b3e0a9
./thatch -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --limit 6 14b1d6e HEAD
./thatch HEAD :worktree
```

Python 3.10+, stdlib, git. Vendored `whenline` from tenure. Exit 0 if the trees differ, 1 if identical, 2 on error. `--no-occupy` is covering only. `--walks` prints `tenure FILE:LINE` lines (pin from the true-side snapshot). Occupancy itself detaches stack identity from the walk end, so an island file that `git log -- path` cannot see still gets eras.

## Empirical transcript

### Before the improvement

Synthetic fixture already did the joint: `t1` vs `t2` was **one** `move` of `given ready | if x > 0` occupying `src/git.py:parse` then `src/parse.py:parse`. Sheaf on the same pair is two exists. `--boolean` recovered `FT`. Sibling line did not split functions grain. TOKEN_A in `keep.txt` was silent. `計画.md` unexplained (not a path-condition).

kizu `3b3e0a9^` vs `3b3e0a9` already named the split as occupancy of a stack, not of a path:

```
AB  move  given bytes.first()==Some(&b'"') | while i<bytes.len() | …
      holders A: src/git.rs:parse_quoted_token
      holders B: src/git/parse.rs:parse_quoted_token
occupy  TRUE 11 commits  holders: src/git.rs:parse_quoted_token
        TRUE  1 commit   holders: src/git/parse.rs:parse_quoted_token
               + src/git/parse.rs:parse_quoted_token
               - src/git.rs:parse_quoted_token
```

sitbone birth `14b1d6e^` vs `14b1d6e` named `guard totalTime>0` occupying `FocusRiverView.swift`. Occupy: FALSE 11 / TRUE 1. Same shape as held, but the predicate is the stack.

sitbone island `14b1d6e` vs HEAD `--limit 6` did **not**. Occupancy-greedy AB-first (sheaf v1's trap, now on stacks) filled the budget with generic holder-spreads. `else` occupied three files on A and more on B. `guard totalTime>0` was classified **AB** because SiteObserver still has that guard on HEAD. `if app.flowScore > 0.2` — the island's own stack — never entered the set.

```
AB  spread  else
AB  move    guard totalTime>0 | guard-else totalTime>0
            holders A: FocusRiverView.swift
            holders B: SiteObserver.swift
AB  spread  guard let app = NSWorkspace.shared.frontmostApplication
AB  move    while !Task.isCancelled
B   exclusive_b  for _ in 0..<3
B   exclusive_b  guard let frame = await frameProvider.captureFrame()
# no exclusive-A flowScore. git log -- FocusRiverView.swift is empty.
```

`for _ in 0..<3` is not a covering primitive. A copied `guard totalTime > 0` that still lives on HEAD must not spend the deleted file's slot. That is tell `--cover`'s occupancy trap, now the *product*.

### After the improvement

Forced by sitbone island, not polish.

1. **Exclusive sides first.** `--limit` is the total size. The smaller exclusive side is reserved 1–2 slots so a one-file island cannot be dropped. AB moves fill leftovers (changed files, true `git.rs → parse.rs` splits).
2. **Junk frames drop out of the covering universe.** Bare `else` / `guard-else` / `for _` are not path-conditions.
3. **Quality.** Characteristic file-moves (path stems changed, few files, name-like or deep) rank 0. Copied-guard spreads rank last. Deeper body stacks beat prefix `given ready` in exact cover (sheaf wanted short greps; a prefix is not the body).
4. **Per-stack `--full`.** v1 treated "tree A is off first-parent" as a walk flag for every member. Exclusive-B stacks that only live on HEAD walked sitbone's 100-commit full history. `--full` is a property of *this stack's* true side.

Same island command:

```
A   exclusive_a  given ¬(app.flowScore>0.2) | given ¬(app.flowScore<-0.2)
                 holders A: FocusRiverView.swift
B   exclusive_b  guard let frame = await frameProvider.captureFrame()
B   exclusive_b  guard let self | given ¬(fresh) | if isFirst | …
…
walk  tenure -C sitbone --full --rev 14b1d6e Sources/SitboneUI/FocusRiverView.swift:…
```

`git log -- FocusRiverView.swift` is empty. The thatch named the stack and occupied it from HEAD with a pin reconstructed from tree A. Tenure handed `HEAD:FocusRiverView.swift:line` would fail; sheaf would have printed `perch --full grep FocusRiverView`.

kizu split is unchanged as occupancy (still the money shot). Fixture move is unchanged.

`./thatch --selftest` — 19 passed. `./demo.sh` — **23 passed, 0 failed** (island assertion now also checks exclusive-B walks stay first-parent). Generated `tenure` line actually ran.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic fixture | stack move `git.py→parse.py`; sibling line; production guard-growth; island vs 8-module flood; TOKEN_A; `計画.md`; `:worktree` |
| `kizu 3b3e0a9^..3b3e0a9` | four-given / quoted-token stack occupied `git.rs`, then `parse.rs` |
| sitbone `14b1d6e^..14b1d6e` | FocusRiverView birth |
| sitbone `70ec7df^..70ec7df` | FocusRiverView death |
| sitbone `14b1d6e` vs HEAD `--limit 6` | island; `git log -- path` empty; exclusive-A reservation |
| sitbone PresenceArbiter vs its birth parent | `guard isEnabled` occupants vs `SitboneCore.swift` mention |

Read-only on the real repos.

## Surprises

- Shortest *set of stacks* is not shortest *predicate*. Exact cover of one file preferred prefix `given ready` until depth was a key. Sheaf's length-min is the wrong secondary key here.
- A copied guard (`totalTime > 0` now in SiteObserver) *is* a real holder move. It is the wrong covering member for a deleted file that still has a unique stack (`flowScore`). Exclusive-A reservation is what keeps the island's own question.
- Tenure's pin is a worktree/`--rev` blob. Two trees give you the stack identity without the file existing at the walk end. That is the joint: occupy a covering member, not a path that `git show HEAD:…` can open.
- kizu's headline move on `--limit 6` is `if !output.status.success()` (many git helpers) plus `parse_quoted_token`. Tenure's money-shot pin `parse.rs:60` (unquoted `b_prefix_start` givens) is a *different* stack on the same file pair; shortest set already covered those paths. Characteristic and shortest still fight.
- `else` occupying three Swift files on both sides looks like a move. It is occupancy of a keyword.

## Failures

1. **Mention echoes are loud** on kizu (`src/app.rs` … `layout.rs` every TRUE era of `status.success()`). They are correctly not holders; they still flood. `--echo no|mention` would help.
2. **`--full` is per stack now**, but a move whose A-side holders sat on a merged-in branch still walks first-parent of HEAD and can miss them. Historical pin of the *other* tree is a mutation.
3. **Birth covering** of FocusRiverView is `guard totalTime>0`, not `flowScore`. One file, one slot; the copied-later guard is exclusive at birth. Honest, not the name a human types.
4. **Match-arm / `if let` / Swift `guard-else` pairing** inherited from `when`. `guard totalTime>0 | guard-else totalTime>0` is one key, not two.
5. **Non-source delta** (計画.md, lockfiles, binaries) stays unexplained. That is the object, not a bug.
6. **Walk lines** name `tenure` on PATH. Demo rewrites the token to a worktree binary. A machine without it still gets a pasteable line that will fail.
7. **Full-tree stack discovery** parses every source blob on both sides. Fine for sitbone/kizu, not argued for a monorepo.

## Suggested mutations

- `--echo no|mention|related` to quiet kizu `app.rs`.
- Prefer the deepest name-like stack on an exclusive file, not the first that covers it (`flowScore` at birth).
- Pipe the thatch into tenure (`thatch A B | tenure --stdin`).
- Cache probes `(sha, cond_key, grain)`.
- `--prefix` so extra frames still count as occupying a parent stack.

## Flipped assumption: bought and lost

Sheaf assumed the covering members are unary grep/exists. Tenure assumed the user already has `FILE:LINE`. Concatenation assumes token occupancy *is* stack occupancy.

**Bought**

- The output is a set of stacks that cover the delta. You do not re-rank a grep catalog, then invent a pin.
- A file move is one member. `git.rs:parse_quoted_token` → `parse.rs:parse_quoted_token` is not two exists.
- Exclusive-side reservation keeps the island's unique stack under a size budget that occupancy-greedy spends on HEAD `else`.
- Occupancy detaches identity from the walk end. The island file is gone at HEAD; the stack still gets eras.

**Lost**

- The grep catalog is hidden. Some true tokens never print.
- Time is still tenure's job; thatch names the stacks and occupies them, it does not invent a new era algebra.
- Shortest set will pick `parse_quoted_token`'s deep quoted-form stack over `parse.rs:60`'s unquoted givens when both cover the same files.
- "Path-condition" will not cover markdown, lockfiles, or binary-only modifies.

## Kill / keep

**Keep.** It is not `sheaf --cover` with extra `tenure` echo. On the first real deleted-file island it emitted an exclusive-A `flowScore` stack and occupied it `--full` without being told the name, the pin, or `--full`. On the first real Rust split it emitted one move `git.rs → parse.rs`, which sheaf cannot name. The v1→v2 change was forced by sitbone island output, not polish.

Kill only if a later generation proves that `sheaf A B` plus a hand-written `tenure FILE:LINE` recovers the move *and* the island pin — it does not, because discovering that the covering member *is* a stack (same cond_key, different holders), and occupying a stack whose file is gone at HEAD, is the object.
