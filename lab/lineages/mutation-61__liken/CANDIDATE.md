# mutation-61 — liken

## Primitive

Given a unified diff, overlay it in memory onto `-C repo` and emit the **added lines that share a path-condition stack** — the invert of graft's default "print the stack of each added line". `--same-as 'fn parse_header | given starts_with(a/)'` or `--same-as FILE:LINE` (post-image) names the stack; fallthrough `given` from early-return guards is included. The worktree is never written.

## Why this might not exist

`graft` (mutation-35) flipped the locus to the post-image and still answers graft's question: *when does this `+` line run?* Reviewers of an unapplied patch then ask the other half: *what else in this hunk shares that `given`?* They reconstruct it by scrolling, now with the extra lie that post-image coordinates are HEAD.

`under` / `ambit` / `amid` invert `when` on **HEAD** locator streams. They do not overlay. `graft --group` clusters, but you cannot address a stack (`given starts_with(a/)`) or a post-image pin and get the siblings. Nothing takes the patch as the object, the post-image as the file, and the stack as the query.

Not leftover-name hunting. Not a third `ambit`/`amid` clone. Not `git apply && when`.

## How to run

```bash
./liken --base :wt --diff fixtures/kin.diff --same-as 'fn parse_header | given starts_with(a/)'
git diff A B -- src/git/parse.rs | ./liken -C kizu --base A --same-as src/git/parse.rs:60
git diff A B -- PresenceArbiter.swift | ./liken -C sitbone --base A --same-as 'guard isEnabled'
./demo.sh
```

Python 3.9+, stdlib only. `./liken` is the CLI. stdin = unified diff. Exit 0 found, 1 none, 2 usage.

## Empirical transcript

### Before the improvement (this first commit)

Tree-shaped brace engine (not graft's streaming snapshot). Source-slice predicates (`len < 5 + 2`, not `len<5+ 2`). Nested-total quoted-form `if` becomes `given ¬(bytes.starts_with(b"\"a/"))`.

`fixtures/kin.diff` (brand-new file, no pre-image):

```
$ ./liken --base :wt --diff fixtures/kin.diff --same-as 'fn parse_header | given starts_with(a/)'
same-as fn parse_header | given starts_with(a/)
shared fn parse_header(bytes: &[u8]) -> Option<usize> | given ¬(bytes.starts_with(b"\"a/")) | given ¬(bytes.len() < 7) | given bytes.starts_with(b"a/")
n      3  files=1
    L11   + let a_side = 1;
    L12   + let b_side = 2;
    L13   + Some(a_side)
```

`return Some(1)` under the quoted-form `if` is absent. `fixtures/kin.rs` is never created.

kizu `src/git/parse.rs` birth (`git diff 3b3e0a9^ 3b3e0a9 | liken --base 3b3e0a9^ --same-as 'given starts_with(a/)'`): `let a_side` (L54) and `let b_side` (L60) group together; `return Some(bytes_to_path(&b_decoded[2..]))` does not. Worktree porcelain unchanged.

The same pipe with `--same-as src/git/parse.rs:60` is *under*, not *same*: nested `if a_side != b_side { return None }` rides along because those frames are a superstack of line 60. Explain reprints the five givens once per subgroup. `--payload` is opt-in, so comments (`// b_prefix_start…`) sit next to the lets.

sitbone hysteresis (`e9b0f75` vs `^`): `--same-as 'guard isEnabled'` is exactly `let status = applyHysteresis(smoothedScore: smoothedScore)` under `guard isEnabled | guard !active.isEmpty`. `precondition` in `init` does not leak. `--same-as 'case .present'` is the `absentThreshold` return, not the other arm.

`./demo.sh` exits 0.

### After the improvement (this commit)

kizu `--same-as src/git/parse.rs:60` was the name lie: *under* that stack, not *same as*. Nested `if a_side != b_side { return None }` rode along. Pins are now **exact** (`--under` restores superstack). Line 60 is one payload line:

```
same-as src/git/parse.rs:60
shared … | given bytes.starts_with(b"a/") | given bytes.get(…) == Some(b" b/")
n      1
  [same]
    L60   + let b_side = &bytes[b_prefix_start + 3..];
```

Explain reprints the shared stack **once**. Extra frames are deltas. `--payload` is default on human output, so the `// b_prefix_start` comment and closing `}` drop. Snippet query still groups the two survivors plus deeper arms, without repeating the four givens:

```
$ git diff 3b3e0a9^ 3b3e0a9 -- src/git/parse.rs \
    | ./liken -C kizu --base 3b3e0a9^ --same-as 'given starts_with(a/)'
same-as given starts_with(a/)
shared fn parse_diff_git_header(rest: &str) -> Option<PathBuf> | given ¬(bytes.starts_with(b"\"a/")) | given ¬(len < 5 + 2) | given inner.is_multiple_of(2) | given bytes.starts_with(b"a/")
  in     parse_diff_git_header(rest: &str) -> Option<PathBuf>
  given  ¬(bytes.starts_with(b"\"a/"))  (L25)
  given  ¬(len < 5 + 2)  (L43)
  given  inner.is_multiple_of(2)  (L47)
  given  bytes.starts_with(b"a/")  (L51)
n      8  files=1

src/git/parse.rs  [post]
  [same]
    L54   + let a_side = &bytes[2..2 + p];
    L56   + let b_prefix_start = 2 + p;
  + given bytes.get(…) == Some(b" b/")
    L60   + let b_side = &bytes[b_prefix_start + 3..];
```

Quoted-form `return Some(bytes_to_path(&b_decoded[2..]))` still absent. Porcelain still empty. `./demo.sh` exits 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu` `src/git/parse.rs` birth (`3b3e0a9`) | `--same-as 'given starts_with(a/)'` groups `let a_side` + `let b_side`; quoted-form excluded; overlay clean |
| `kizu` `src/git/parse.rs:60` pin | other added lines under that post-image stack |
| `sitbone` `PresenceArbiter.swift` hysteresis (`e9b0f75`) | `--same-as 'guard isEnabled'` vs `init` / `case .present` |
| `fixtures/kin.diff` | two lets share `given a/`; quoted `return Some(1)` does not; no `kin.rs` on disk |
| `fixtures/newif.diff` | overlay of an `if` that does not exist in HEAD |
| `fixtures/hyst.diff` | two added lines under Swift `guard isEnabled` |
| `fixtures/insert.diff` | Python `audit.block` under `if not user.can_delete` |
| `fixtures/mismatch.diff` | unplaced → exit 1 |

Read-only on the real repos. Overlay never writes them.

## Surprises

- The valuable invert on an *unapplied* patch is not "group by `git diff -W` function." It is "name the `given` that only exists after the hunks above this one have been applied." Overlay of the whole file, not the hunk window, is still the primitive; the query is the new verb.
- Source-slice predicates fall out of a tree parser for free (`len < 5 + 2`). graft's token-join was a rendering accident, not part of the invert.
- `--same-as FILE:LINE` meaning *under* (superstack) is the honest path-condition, and the wrong name. Usage of parse.rs:60 wants the other line at that stack, not the nested `return None`.

## Failures

1. **Snippet `--same-as 'given starts_with(a/)'` is still under.** Deeper `if a_side != b_side` arms remain in the group (they *do* run given `a/`). Pins no longer have this lie.
2. **Match-arm total-exit** is conservative (same family as the parents).
3. **Combined / binary diffs** are unplaced (exit 1), not guessed.
4. **`--base HEAD` vs `git diff` (index).** Unstaged diffs whose pre-image is the index need `--base :wt` or `git diff HEAD`. Documented, not inferred.

## Suggested mutations

- `--exact` as the FILE:LINE default; keep subsequence for snippet queries.
- Feed `--same-as` groups into a review TUI (kizu hunks tagged by post-image condition).
- `--also-context` to show the surviving *old* lines under the same stack, not just `+`.
- Address a stack and jump to today's line numbers *or* the post-image's.

## Kill / keep

**Keep**, if the invert stays a query on the overlay. Kill if a later generation reduces it to `graft --group` with a grep, or to "run `when` after `git apply`."
