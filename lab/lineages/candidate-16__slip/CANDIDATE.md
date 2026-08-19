# candidate-16 — slip

## Primitive

A `file:line` address is relocatable: rewrite a stale locator from one snapshot of a codebase onto another by content fingerprint (line + identifiers + neighbors + split-directory path affinity), not by git blame or VCS identity.

## Why this might not exist

Developers constantly hold dead pointers: CI logs from last night's SHA, a stack trace from production, a review comment that says `src/app.rs:142`, a pytest traceback, a note in a ticket. `git blame` points backward. `git blame --reverse` can crawl a line forward but dies on copies, splits, signature drift, and anything that is not git. `patch` fuzz is for hunks, not addresses. Source maps are for minifiers.

Nobody shipped a Unix filter whose only job is: **take a stream of locators from tree A, emit them as locators in tree B.** That is the missing verb.

(Four primitives considered. Discarded as too conventional: test-vs-production edit lag; residue-of-deleted-symbols / afterimage. The other unusual leftover is `soul` — match files across a language rewrite by rare-token fingerprint; see mutations.)

## How to run

From the worktree root:

```bash
chmod +x ./slip
./slip --help
./demo.sh
./slip --repo /path/to/repo --from <old-sha> --to HEAD path:line
cat compiler.log | ./slip --repo /path/to/repo --from <old-sha>
./slip --from-dir old/ --to-dir new/ path:line --porcelain
```

Exit 0 on success. `--strict` exits 1 if a locator cannot be read from the source snapshot. Confirmed deletions are answers, not errors.

## Empirical transcript

### Working software (v0.1)

Synthetic ugly repo (nested git, unicode path, split/rename/delete) plus real kizu:

```
$ ./slip --repo $UGLY --from $V1 --to $V2 --porcelain src/calc.py:14
moved	src/calc.py:14	src/math/ops.py:8	0.744	path or surrounding file changed

$ ./slip --repo $UGLY --from $V1 --to $V2 --porcelain src/calc.py:7
edited	src/calc.py:7	src/math/sauce.py:3	0.537	line text drifted

$ ./slip --repo $UGLY --from $V1 --to $V2 --porcelain src/calc.py:11
deleted	src/calc.py:11	-	0.000	no candidates

$ ./slip --repo kizu --from b4e6a5d --to HEAD --porcelain src/app.rs:529
moved	src/app.rs:529	src/app/layout.rs:17	0.927	path or surrounding file changed

$ ./slip --repo kizu --from b4e6a5d --to HEAD --porcelain src/app.rs:543
moved	src/app.rs:543	src/app/navigation.rs:22	0.927	path or surrounding file changed

$ ./slip --repo kizu --from b4e6a5d --to HEAD --porcelain src/app.rs:602
edited	src/app.rs:602	src/app/layout.rs:35	0.797	line text drifted
# old: pub fn hunk_fingerprint(hunk: &crate::git::Hunk) -> u64 {
# new: pub fn hunk_fingerprint(hunk: &Hunk) -> u64 {
```

kizu `src/app.rs` was a 9480-line godfile split in `f1ae3c2` into `layout.rs` / `navigation.rs` / `text_input.rs` / …. `git log --follow -L` refuses (`--follow requires exactly one pathspec`). slip still lands the address.

### Failures recorded against v0.1

Same kizu SHA, a mixed real-world log. v0.1's regex required `dir/file.ext:line` and did not bind against known paths:

```
$ cat kizu-log.txt
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
  File "src/app.rs", line 543, in nearest_landing_forward
LICENSE:1: copyright

$ cat kizu-log.txt | ./slip --repo kizu --from b4e6a5d --to HEAD     # v0.1
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app.rs:529:5
  File "src/app.rs", line 543, in nearest_landing_forward
LICENSE:1: copyright
```

Nothing slipped. Absolute CI prefix, Python `File ", line` grammar, extensionless `LICENSE` / `justfile` / `Makefile`, colon in filenames (`src/weird:colon.py:1` parsed as `colon.py:1`), spaces in filenames — all silent pass-throughs. Also: exact identity on voidtrace scored 0.780, not 1.000, because neighbor/token weights punished a unique header line. Deleted `doomed()` reported `no candidates` with no neighborhood.

### After the improvement (v0.2)

Locator scan is longest-known-path in the source snapshot, plus Python traceback grammar, plus suffix-bind of absolute paths. Exact copies short-circuit to 1.0. Deletions name surviving anchors.

```
$ cat kizu-log.txt | ./slip --repo kizu --from b4e6a5d --to HEAD     # v0.2
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
  File "src/app/navigation.rs", line 22, in nearest_landing_forward
LICENSE:1: copyright

$ ./slip --repo voidtrace --from HEAD --to HEAD --porcelain packages/kernel/src/evaluate.ts:1
same	packages/kernel/src/evaluate.ts:1	packages/kernel/src/evaluate.ts:1	1.000	

$ ./slip --repo $UGLY --from $V1 --to $V2 --porcelain src/calc.py:11
deleted	src/calc.py:11	-	0.000	last context at src/math/sauce.py:4; next context at src/math/ops.py:8

$ printf '  File "src/calc.py", line 3, in add\n' | ./slip --repo $UGLY --from $V1 --to $V2
  File "src/math/ops.py", line 3, in add

$ printf '/home/runner/work/ugly/ugly/src/calc.py:14: error\n' | ./slip --repo $UGLY --from $V1 --to $V2
/home/runner/work/ugly/ugly/src/math/ops.py:8: error
```

kizu `edit_insert_str` was reported "gone" by a naive `fn ` name diff (`fn` vs `pub(crate) fn`). slip still mapped `src/app.rs:635` → `src/app/text_input.rs:17` (edited, 0.895).

## Dogfood targets

- Synthetic ugly git repo built by `./demo.sh`: split+rename, signature drift, deletion, unicode `src/日本語.py`, `src/weird:colon.py`, `notes/file with spaces.txt`, extensionless `Makefile`, nested git under `vendor/nested`.
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — 9480-line `src/app.rs` split at `b4e6a5d`/`f1ae3c2`; mixed rustc/CI/Python/LICENSE log.
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — HEAD identity on `packages/kernel/src/evaluate.ts:1`.
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `KinsokuEngine.swift:12` `transform` from first commit `a41089c` to HEAD (still line 12, score 1.000).
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — `stratal/SKILL.md`. Out-of-range line against a 6-line first blob correctly unresolved (the 615-line "file" was a `git show $sha` patch, not the blob). Heading `# Stratal` at `fca03d8` still `stratal/SKILL.md:6`.

## Surprises

- File-split into a directory of the same stem (`src/app.rs` → `src/app/*.rs`) is common and is *not* a git rename; a stem-prefix bonus in path scoring is what makes the kizu case fall out.
- `git log --follow -L :symbol:path` is the "obvious" tool and it errors on the exact case slip is for.
- Silent pass-through on stdin is worse than a loud parse failure: v0.1 "worked" (exit 0) on a CI log and rewrote nothing.
- A first-commit path from `git log --reverse -- path` can be a tiny blob; slip's out-of-range rejection saved us from mapping a hunk header that never lived in that tree.

## Failures

- Common/`}`-only lines refuse to fingerprint (`unresolved`: too trivial). Correct, but annoying for "go to the closing brace of this function."
- Two identical helpers in dest can still confuse the scorer; path affinity usually wins, not always.
- Stdin locators are bound to the *source* snapshot. A log that mixes old paths and new paths needs the old SHA in `--from`; new-only paths (a `justfile` added after the SHA) will not parse.
- Whole-tree index of kizu (thousands of e2e fixtures) is acceptable but not free; no incremental cache yet.
- Nested git in the demo still makes `git add` warn if you add it; discovery itself is fine with `--repo`.

## Suggested mutations

- `slip --watch`: keep a pinfile of locators and rewrite it on HEAD movement (scar-review companion for kizu).
- Emit a stable pin (`slip mint`) that is the fingerprint itself, not path:line, so tickets can store `pin:…` instead of `file:line@sha`.
- `soul`: rare-token file identity across language rewrites (Python tree ↔ Rust tree) using the same index.
- Hunk-level slip: relocate a failing `git am` patch by slipping each hunk header.
- Coverage/profile maps: rewrite `file:line` in lcov/profraw onto another commit so coverage can survive a refactor.

## Kill / keep

**Keep.** The interaction is one verb, Unix-composable, empirically hits a case (`app.rs` split) that git's own line-follow cannot, and got sharper from real log grammars rather than from imagined features. Not a wrapper: blame is never called. Kill only if a later generation proves pins-as-objects (`slip mint`) is the actual primitive and this filter is just a backend.
