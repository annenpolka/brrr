# mutation-35 — graft

## Primitive

Path-condition stack on the **post-image of an unapplied patch**: given a unified diff, overlay it in memory onto `-C repo` and emit the nested predicates each added line would run under — including fallthrough `given` from early-return guards — without writing the worktree.

The locus is not in HEAD. `git diff -W` names the function. Unified hunks are windows. The `if` that makes a change legal is often above the `@@`, and a `+` line's number only exists after apply.

## Why this might not exist

`when` (candidate-20) and `whence` (reimpl-04) answer "whence this line runs" on the current tree. Both listed the same mutation: overlay an unapplied patch so `--diff` is the post-image. Their `--diff` maps `+` coordinates onto the working tree, which is lucky when the insert stays in the same arm and lying when the patch *introduces* the `if`.

Reviewers still reconstruct enclosing predicates by scrolling, now with the extra lie that the line numbers in the hunk are HEAD line numbers. Nothing takes the patch as the object and the post-image as the file.

Not leftover-name hunting. Not an LSP. Not a second `when` clone: HEAD-only is `--now` opt-in.

## How to run

```bash
./graft --base :wt --diff fixtures/newif.diff --explain
./graft --now fixtures/quoted.rs:32 --explain
git diff A B -- src/git/parse.rs | ./graft -C kizu --base A --tsv
./demo.sh
```

Python 3.10+, stdlib only. `./graft` is the CLI.

## Empirical transcript

### Before the improvement (first overlay, simple-exit `given` only)

`fixtures/newif.diff` already proved the overlay: HEAD's `guards.rs:11` is `let p = ...`; after apply, line 11 is `if bytes.len() > 100` and line 12's `return None` sits under that `if`. `when --diff` reports `let p` at those coordinates.

kizu `src/git/parse.rs:60` sandwich (`git diff 3b3e0a9^ 3b3e0a9 | graft --base 3b3e0a9^`) matched `when` at B on the four simple-exit givens (`len<5+2`, `inner.is_multiple_of(2)`, `starts_with(b"a/")`, `b/` separator) and **missed** the quoted-form `if bytes.starts_with(b"\"a/") { ... nested if ... return Some }` — same conservative hole both parents recorded.

sitbone `PresenceArbiter` hysteresis (`e9b0f75` vs `^`): `let status = applyHysteresis(...)` correctly under `guard isEnabled | guard !active.isEmpty`, but added `precondition(...)` inside `init` was attributed to the class because Swift `init(` is not `func`.

### After the improvement (this commit)

1. **Nested-total early returns.** A closed `if` becomes `given ¬P` when the *last statement* of the block is a total exit, even if nested `if`s sit above it. parse.rs:60 now carries five givens:

```
in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
given  ¬(bytes.starts_with(b"\"a/"))
given  ¬(len<5+ 2)
given  inner.is_multiple_of(2)
given  bytes.starts_with(b"a/")
given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")
here   let b_side = &bytes[b_prefix_start + 3..];
depth=6
```

`when` / `whence` on the same locus still report depth=5.

2. **Swift `init`.** sitbone sandwich now places `precondition(presentThreshold > absentThreshold)` `in init(...)`.

Sandwich vs `when` at B for `return smoothedScore < absentThreshold` is identical (`switch previous | case .present`). graft is a *superset* on parse.rs:60 (the extra quoted given).

`./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu` `src/git/parse.rs` birth (`3b3e0a9`) | sandwich: graft of `git diff A B` against A vs `when` at B; quoted-path given |
| `kizu` `src/git/diff.rs:51` | `given success` + `given raw.is_empty()` (matches `when`) |
| `sitbone` `PresenceArbiter.swift` hysteresis (`e9b0f75`) | added line in `detect()` under two `guard`s; new `applyHysteresis` `case .present` |
| `tenaoshi` `EditPlanComposer.swift:69` | `case .invalidRange(...)` not the first `case` |
| `voidtrace` `compare.ts:84` | `for` + two empty-check `given`s + `if` |
| `fixtures/newif.diff` | overlay of an `if` that does not exist in HEAD |
| `fixtures/quoted.rs` | nested-total quoted-form `given` |
| `fixtures/newfile.diff` | brand-new file, no pre-image |
| `fixtures/mismatch.diff` | unplaced → exit 1 |

Read-only on the real repos. Overlay never writes them.

## Surprises

- The valuable "when" on an *unapplied* patch is not "the function `git diff -W` named." It is the predicates that only exist after the hunks above this one have been applied. Overlaying the whole file, not the hunk window, is the primitive.
- Nested-total `given` is one last-statement check. `when`'s simple-exit heuristic refused any nested `if`; Python already did the last-stmt thing; braces just had to match.
- Swift `init(` is a function with no name token after the keyword. Dogfooding sitbone's hysteresis commit surfaced it immediately: every added `precondition` looked class-scoped until `init` was a `fn` frame.
- `when --diff fixtures/newif.diff` prints the *old* `let p = ...` at the new line numbers. That is not a parser bug. It is the HEAD-locus assumption, in one row of TSV.

## Failures

1. **Token spacing.** `len<5+ 2` instead of `len < 5 + 2`. Same family as the parents.
2. **Closing-brace snapshot.** The `}` of a total-exit `if` can appear under the `given` that the close just created. Harmless, slightly noisy.
3. **Match-arm total-exit** is conservative. Quoted-path did not need it.
4. **Combined / binary diffs** are unplaced (exit 1), not guessed.
5. **`--base HEAD` vs `git diff` (index).** Unstaged diffs whose pre-image is the index, not HEAD, need `--base :wt` or `git diff HEAD`. Documented, not magically inferred.

## Suggested mutations

- Address a locus as a condition path (`graft 'fn parse_header | given starts_with(a/)'`) and jump to today's *or* the post-image's line numbers.
- Invert: lines in the patch that share a stack (`graft --same-as`).
- Feed `--group` into a review TUI (kizu hunks tagged by post-image condition).
- Apply with fuzz comments (`#` context in rust) so commented-out context still places.

## Kill / keep

**Keep.** The flipped assumption (the locus is the post-image) is small, pipeable, and changed what we could say about a kizu introducing-commit and a sitbone hysteresis hunk *before they land*. Kill only if a later generation reduces it to "run `when` after `git apply`."
