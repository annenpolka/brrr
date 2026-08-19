# mutation-35 — ambit

## Primitive

Name a predicate snippet; emit every locus whose path-condition contains it, **scanning the files stdin locators named** (`rg | ambit`). Reverse of `when`, mutation of `under`: the object is still a condition stack; the default producer is a locator stream, not a tree walk.

## Why this might not exist

`under` already inverted `when`: name a condition, print the lines. Its default was `scan_paths(cwd)` — a skip-listed rglob — with stdin as an optional *line filter*. That is the wrong object twice.

1. Walking a tree is `rg`'s job. `under 'isEnabled'` from a random cwd is a silent full-tree parse. `sluice` already killed this for inverse-printf; path-condition invert kept the walker.
2. Filtering grep *lines* is the opposite of the invert. The valuable loci (fallthrough `given bytes.starts_with(b"a/")` at `let b_side`) **do not mention the predicate**. `rg 'starts_with' | under --filter` cannot see them. The locators should name the *file to scan*.

`rg | ambit 'starts_with(a/)'` is the pipe: rg chooses files (and, for `-n`, a fingerprint of lines); ambit scans those files for the ambit of the condition; hits stream per file.

Not leftover-name hunting, not inverse-dead-code, not "grep the `if` and print the body."

## How to run

```bash
./ambit 'user.locked' fixtures/nested.py --explain
printf '%s\n' 'fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {' \
  | ./ambit 'starts_with(a/)' --explain
rg -l --type rust 'starts_with' kizu | ./ambit --kind given 'a/'
cd kizu && rg -n 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --explain
rg -nH 'return None;' parse.rs | ./ambit --kind given 'a/' --hits --tsv
./ambit 'can_delete' --diff fixtures/sample.diff --group
./demo.sh
```

Python 3.10+, stdlib only. `./ambit` is the CLI. Exit 2 if you pass a directory without `--walk` or invoke with no files and no locators — there is no cwd walk.

## Empirical transcript

### Before the improvement (commit `460c0fa`)

Fixtures already inverted `when`: `user.locked` hit `return "denied"` not `return "drained"`; `isEnabled` skipped the Swift guard-else; stdin `FILE:LINE` **scanned** `guards.rs` and emitted `let p` even though rg only printed the inverted `!starts_with` arm. `./ambit 'user.locked'` with no files exited 2 (`No cwd walk`). `--hits` restored the ancestor line filter.

Real kizu lied about *which file*.

```
$ rg -n 'return None;' kizu/src/git/parse.rs | ./ambit --kind given 'a/'
# single-file rg emits LINE:text, no path
ambit: stdin is not a diff or file:line stream
# rc=2
```

Same footgun `when` had, and the mutation's own default (`rg | ambit`) is exactly that pipe. Passing `-nH` or repeating FILE worked and already produced the invert of `when parse.rs:60`:

```
parse.rs:59-60
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

…plus a trailing span whose `here` was a lone `}` (collapse picked the first equal-score line in `63-65`).

`--hits` on the same `return None;` stream kept only L58 and L62 — the returns that actually run under `given a/`. Scan kept `let b_side`, which rg never printed. That is the flip, working, once the file is known.

### After the improvement (this commit)

LINE:text locators are a partial image of a file. Matching `(line, text)` pins against git-listed sources (cwd / `--repo`) recovers the file if unique. Collapse prefers a payload line over `{` / `}`.

```
$ cd kizu
$ rg -n 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --explain
```

Same five spans as `--kind given 'a/' parse.rs`, including `let b_side`, without repeating the path and without `-H`. The last span is now:

```
parse.rs:63-65
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  given  a_side== b_side
  here   Some(bytes_to_path(a_side))
```

From the ambit worktree, `--repo $KIZU` recovers the same file. `--hits` still answers the other question: which of *these* returns sit under `a/` (L58, L62 only).

`sitbone` `under isEnabled` / `voidtrace` `actual.has` polarity are unchanged (inherited matcher).

`./demo.sh` exits 0 (24 tests + fixtures + kizu parse.rs).

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs` | `rg -n 'return None;'` / `starts_with` → `--kind given 'a/'` (scan vs `--hits`) |
| `kizu/src/git/diff.rs` | `--kind given 'success'` via locator stream |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | adversarial nesting + stdin file-name vs line-filter |
| `fixtures/sample.diff` | `--diff` still a line filter (the patch *is* the locators) |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- The invert is unusable as `rg | tool` until locators name **files**. Filtering rg hits is a grep of lines that already mention something; the `given` survivors never will.
- Single-file rg omitting the filename is not a parser bug, it is the default. Recovering the file from `(line, text)` pins against `git ls-files` is the same object as the locators, not a walker: we never parse a file until uniqueness is known.
- Collapse `here }` on parse.rs:63-65 was not an engine miss. `}` and `Some(...)` tied on payload score; the first line won. Scoring brace-only as 0 is the whole fix.
- `--repo` is a *search root for pin recovery*, not a scan root. Passing kizu as a DIR operand still exits 2 without `--walk`.

## Failures

1. **Inherited engine holes.** Nested-but-total early returns (quoted-path `if bytes.starts_with(b"\"a/") { … return Some }` is not `given ¬(quoted form)` at line 60), `if let` dropping `let`, `len<5+ 2` spacing, empty Rust match-arm preds — same as `when` / `under`.
2. **Pin recovery needs a tree of names.** `rg /abs/parse.rs | ambit` from another repo still fails unless `--repo` / FILE / `-nH`. We will not rglob the disk.
3. **Ambiguous pins.** Two files with the same text at the same line numbers → recovery refuses (exit 2), does not guess.
4. **`--diff` of an unapplied patch** maps `+` onto the working tree. Same hole as `when`.
5. **`if not P` vs `!P`.** Python `if not user.can_delete` stays a written predicate. Rust/JS `!P` is inverted. Inherited, easy to miss.
6. **Locator buffer.** Hits stream per file; the rg stream itself is collected (it is small). `--group` still buffers hits.

## Suggested mutations

- Overlay an unapplied patch so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting nested ifs (quoted-form miss on parse.rs).
- Default hide eval-only headers (`if …:`) in addition to brace-only `here`.
- `--same-as` as the only input (drop the snippet): lines that share *exactly* this stack.
- A TUI that paints every line of the recovered file by whether it is in the ambit.

## Kill / keep

**Keep.** The object is the same as `under` / `when`; the verb is now a Unix filter: `rg` picks files, `ambit` names the condition those files run under. Kill only if a later generation walks cwd again or reduces it to "print the grep hits that sit inside an `if`."
