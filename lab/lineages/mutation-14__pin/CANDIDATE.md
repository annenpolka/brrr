# mutation-14 — pin

## Primitive

A code locus is a **pin**: mint a self-contained fingerprint (line + identifiers + in-scope neighbors + nearby def anchors + path hint) once, store the token, and `resolve` it onto any later tree. The object is the pin, not a locator string.

## Why this might not exist

`slip` (candidate-16) relocates `file:line` by fingerprint. Every invocation still needs the locator *and* the source SHA: `slip --from b4e6a5d --to HEAD src/app.rs:529`. Tickets, review comments, and sticky notes cannot hold that. They hold `src/app.rs:529`, which dies the next time the godfile splits.

`git blame --reverse` crawls a line forward and dies on copies and splits. Source maps are for minifiers. IDE breakpoints rebind inside one buffer. Nobody shipped a Unix token you paste into a ticket whose only job is: **this is the address; land it on whatever tree you have now.**

PRIOR_ART named the gap: “Durable pin (expectation attached to a code locus that survives rename).” `slip` relocates; it does not mint.

## How to run

From the worktree root:

```bash
chmod +x ./pin
./pin --help
./demo.sh
./pin mint --repo /path --from <old-sha> path:line
./pin resolve --repo /path --to HEAD pin1.…
./pin resolve --repo /path --to HEAD --file review.pins
./pin show pin1.…
```

Exit 0 on success. `resolve` exits 2 if you hand it a `path:line` (that is a locator; mint first). `--strict` exits 1 if a pin cannot be decoded. Confirmed deletions are answers, not errors.

## The assumption that was flipped

Killed: “the user re-supplies `path:line` (and usually `--from SHA`) every time.”

New: **mint once, resolve forever.** The stored object is `pin1.` + zlib+json of the fingerprint. Resolve takes no locator and needs no origin SHA. Git is optional (`--from-dir` / `--to-dir`).

### Bought

- A pasteable token for tickets, pinfiles, review bookmarks.
- `resolve` refuses locators. The pin is the only address.
- `pin show` dumps the fingerprint without a tree.
- File-split path affinity (`src/app.rs` → `src/app/*.rs`) still works; it lives in the pin’s path hint.
- A named pinfile (`seen\tpin1.…`) resolves by name, still without `path:line`.

### Lost

- Mint still needs a locator *once* (and a snapshot that still contains that line).
- The token is opaque (~200–400 chars). `show` is required to read it.
- No stream rewrite of compiler logs (that is `flume` / `slip` stdin). Pin’s object is the stored address, not the log.

## Empirical transcript

### Working software (v0.1)

Synthetic ugly repo (split+rename, signature drift, deletion, unicode, colon name, spaces, nested git) plus real kizu / voidtrace / tenaoshi. `./demo.sh` exited 0.

```
$ PIN=$(./pin mint --repo $UGLY --from $V1 src/calc.py:14)
$ echo $PIN
pin1.eNptzc0K...
$ ./pin resolve --repo $UGLY --to $V2 --porcelain "$PIN"
moved	-	src/calc.py:14	src/math/ops.py:8	0.794	path or surrounding file changed

$ ./pin resolve --repo $UGLY --to $V2 src/calc.py:14
pin resolve: src/calc.py:14 is a locator; pins are minted tokens, not path:line
# exit 2

$ ./pin show "$PIN"
  minted: src/calc.py:14
  text:   def helper_keep():
  before:
    -     return x ^ MAGIC
    - def doomed():
    -     return "this will be deleted"
```

kizu, mint at `b4e6a5d`, resolve `HEAD` with **no path:line**:

```
$ SEEN=$(./pin mint --repo kizu --from b4e6a5d src/app.rs:529)
$ ./pin resolve --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	0.919	path or surrounding file changed

$ ./pin mint --from b4e6a5d src/app.rs:543 | xargs ./pin resolve --to HEAD --porcelain
moved	-	src/app.rs:543	src/app/navigation.rs:22	0.919

$ ./pin mint --from b4e6a5d src/app.rs:602  # hunk_fingerprint, &crate::git::Hunk
moved/edited → src/app/layout.rs:35  0.797  line text drifted

$ ./pin mint --from b4e6a5d src/app.rs:635  # fn → pub(crate) fn
edited → src/app/text_input.rs:17  0.942
```

`git log --follow -L` still refuses the split (`--follow requires exactly one pathspec`). The pin lands it.

### Failures recorded against v0.1

1. **`pin show` of `helper_keep` included `def doomed()` and `return x ^ MAGIC`.** Neighbor collection walked into the previous function. After the split those neighbors are gone or in another file. The pin was fingerprinting the wrong neighborhood.
2. **`pin --porcelain pin1.… --repo $R --to $V2` printed argparse usage.** Flags before the token did not imply `resolve`. A ticket paste of `pin --repo kizu pin1.…` failed.
3. **Exact unique copies scored 0.762–0.794** (`UNIQUE_TOKEN_QZX` dir-to-dir, `helper_keep` after rename) because path affinity punished a perfect line match.
4. **Blind “exact copy → 1.0” then stole voidtrace identity.** `packages/kernel/src/evaluate.ts:1` is `import {`, as is `apps/cli/src/cli.test.ts:1` and a dozen others. First naive 1.0 short-circuit resolved the pin onto `cli.test.ts`. Common clones need path as tie-break; unique lines (`helper_keep`, `seen_hunk_fingerprint`) should still be 1.0 after a move.
5. **File-order anchors on kizu `app.rs` were `DiffSnapshots, with_cap, contains_key, Iterator`.** First unique defs in a 9480-line godfile, unrelated to line 529. They bloated the token and would not describe a deletion hole.

### After the improvement (v0.2)

- Neighbors stop at a sibling definition and skip the previous function’s body. Attached `///` comments and the current body stay.
- Exact match scores 1.0 only if the line is unique in dest, a rare token from the pin hits, or the path is unchanged. `import {` stays with `evaluate.ts`.
- Anchors are the nearest unique defs, not the first six in the file.
- `pin1.…` anywhere in argv implies `resolve`; flags work on either side.
- `--pretty` dumps the fingerprint on stderr; stdout stays a token.

```
$ ./pin show "$HELPER"
  minted: src/calc.py:14
  text:   def helper_keep():
  unique: helper_keep
  anchors: doomed, secret_sauce
  after:
    -     return "stable helper"
# no doomed() in the neighbor list

$ ./pin resolve --repo $UGLY --to $V2 --porcelain "$HELPER"
moved	-	src/calc.py:14	src/math/ops.py:8	1.000	path or surrounding file changed

$ ./pin resolve --porcelain "$HELPER" --repo $UGLY --to $V2     # flags first
moved	-	src/calc.py:14	src/math/ops.py:8	1.000

$ ./pin resolve --repo $UGLY --to $V2 --porcelain "$DOOMED"
deleted	-	src/calc.py:11	-	0.000	surviving anchors: helper_keep at src/math/ops.py:8; secret_sauce at src/math/sauce.py:3
```

kizu after v0.2 (still no path:line on resolve):

```
$ ./pin show "$SEEN"
  minted: src/app.rs:529
  text:   pub fn seen_hunk_fingerprint(
  tokens: seen_hunk_fingerprint
  anchors: nearest_landing_forward, uses_plus_line_format, nearest_landing_backward, next_sorted_after
  before:
    - /// mismatched fingerprint means the hunk has been edited since it
    - /// was marked seen — in that case the mark is considered stale and
    - /// the hunk behaves as if it were unmarked (auto-expand).
  after:
    -     seen: &BTreeMap<(PathBuf, usize), u64>,
    -     path: &Path,
    -     old_start: usize,

$ ./pin --repo kizu --to HEAD --porcelain "$SEEN"
moved	-	src/app.rs:529	src/app/layout.rs:17	1.000	path or surrounding file changed

$ ./pin resolve --repo kizu --to HEAD --porcelain "$LAND"
moved	-	src/app.rs:543	src/app/navigation.rs:22	1.000

$ ./pin resolve --repo kizu --to HEAD --porcelain "$FP"
edited	-	src/app.rs:602	src/app/layout.rs:35	0.797	line text drifted
# old: pub fn hunk_fingerprint(hunk: &crate::git::Hunk) -> u64 {
# new: pub fn hunk_fingerprint(hunk: &Hunk) -> u64 {

$ ./pin resolve --repo kizu --file kizu.pins --porcelain seen landing
moved	seen	src/app.rs:529	src/app/layout.rs:17	1.000
moved	landing	src/app.rs:543	src/app/navigation.rs:22	1.000
```

voidtrace `evaluate.ts:1` is `same` at 1.000, not stolen by `cli.test.ts`. tenaoshi `KinsokuEngine.swift:12` `transform` from `a41089c` → HEAD is `same` 1.000.

`./demo.sh` exits 0 (selftest + ugly fixture + kizu split + voidtrace + tenaoshi).

## Dogfood targets

- Synthetic ugly git repo built by `./demo.sh`: split+rename, signature drift, deletion, unicode `src/日本語.py`, `src/weird:colon.py`, `notes/file with spaces.txt`, extensionless `Makefile`, nested git under `vendor/nested`.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — 9480-line `src/app.rs` split at `b4e6a5d`/`f1ae3c2`; four pins (seen, landing, hunk_fingerprint, edit_insert_str) plus a named pinfile.
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — HEAD identity on `packages/kernel/src/evaluate.ts:1` must not jump to other `import {` files.
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `KinsokuEngine.swift:12` `transform` from first commit `a41089c` to HEAD (still line 12, score 1.000).

## Surprises

- The pin is smaller than a review comment and actually more stable than `file:line@sha`, because resolve never asks for the SHA again.
- File-split into a directory of the same stem is still what makes kizu fall out; the pin only has to *carry* that path hint.
- `pin show` is not a luxury: without it the token is indistinguishable from a blob hash, and v0.1’s polluted neighbors were invisible until show printed `def doomed()`.
- Common first lines (`import {`, `use std::`) are a different problem from unique defs. Unique-token 1.0 and clone-with-path-tie-break have to coexist or identity is a lie.
- Nearby-def anchors on a godfile (`nearest_landing_forward` next to `seen_hunk_fingerprint`) become cross-file surviving context after the split — useful for deletions, free for hits.

## Failures

- `}`-only and blank lines refuse to mint (`too trivial`). Correct, annoying for “the closing brace of this function.”
- Two identical helpers in dest can still confuse the scorer if neither is unique and path affinity is weak.
- Mint requires a snapshot that still contains the line. A log from a SHA you no longer have cannot be minted unless you can produce `--from-dir` of that tree.
- Whole-tree index of dest on every resolve; no pin cache. Fine for kizu (148 files), not a design for linux.git.
- Token length ~200–430 chars. Tickets accept it; commit messages look ugly.
- Nested git in the demo still makes `git add` warn if you add it; `--repo` discovery itself is fine.

## Suggested mutations

- Attach a note/expectation to the pin (`pin mint --note 'leaks if seen map grows'`) so the token carries the review comment, not just the locus. PRIOR_ART’s original wording.
- `pin watch`: rewrite a pinfile onto HEAD as the tree moves (kizu scar-review companion).
- Hunk-level pin: mint each `@@` header of a failing `git am` patch.
- `soul`: rare-token file identity across a language rewrite, using the same fingerprint fields at file grain.
- Coverage maps: mint every lcov `file:line` once, resolve onto the post-refactor tree.

## Kill / keep

**Keep.** The flipped assumption is visible in the CLI: `resolve` will not take `path:line`, and kizu’s `app.rs` split is landed from a stored token with no origin SHA. v0.2 was forced by real collisions (`import {`) and real neighbor pollution (`doomed()`), not by imagined features. Kill only if a later mutation proves the pinfile-as-registry (short names, repo-local store) is the actual primitive and the self-contained token is just an encoding.
