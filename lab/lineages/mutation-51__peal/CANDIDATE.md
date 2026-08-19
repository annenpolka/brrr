# mutation-51 — peal

## Primitive

Name a locus *from stdin locators* (`rg | peal`); emit other loci whose path-condition is the **same stack**, or a **superset** (deeper nest: the seed stack is an ordered prefix), **scanning the files those locators named**. Control-flow rhyme as a Unix filter. Not a tree walk.

The object is still a **condition stack**. The address is a locator. The match is identity of effective `(kind, pred)` frames, not a snippet.

## Why this might not exist

`chime file:line` answers "what else is in this arm?" and then does the wrong thing with the producer: default scan is the seed's file, optional DIR walk, and stdin is a *line filter*. `ambit` already flipped `under` onto `rg | tool` (files from locators, no cwd walk) but the object is a predicate *snippet*. Reviewers pipe grep because grep found a line, then ask chime's question about *that line's stack*. Nothing is `chime` with `ambit`'s mouth.

1. Walking a tree is `rg`'s job. `chime` from a random cwd with a DIR operand is a silent parse. Path-condition rhyme kept the walker.
2. Filtering grep *lines* is the opposite of the invert. The rest of the arm (`Some(bytes_to_path(a_side))` next to `let b_side`) **does not mention** the rg pattern. `rg 'b_side' | chime --filter` cannot see it. The locators should name the *file to scan* and, when they carry a line, the *seed stack*.

`rg -n 'let b_side' parse.rs | peal` is the pipe: rg chooses files (and, for `-n`, a seed locus); peal scans those files for same/deeper stacks. Hits include statements rg never printed.

Not leftover-name hunting, not inverse-dead-code, not format-string inversion, not `rg` of the `if`.

## How to run

```bash
printf '%s\n' 'fixtures/guards.rs:11:    let p = (bytes.len() - 5) / 2;' | ./peal --explain
./peal fixtures/nested.py:13 --exact --explain
printf '%s\n' fixtures/nested.py | ./peal --same-as fixtures/nested.py:8 --group
printf '%s\n' '13:    return "denied"' | ./peal --exact --tsv
cd "$KIZU" && rg -n 'let b_side' src/git/parse.rs | /path/to/peal --explain
rg -nH 'return None;' parse.rs | ./peal --hits --tsv
./demo.sh
```

Python 3.10+, stdlib only. `./peal` is the CLI. Exit 2 if you pass a directory without `--walk` or invoke with no files and no locators — there is no cwd walk.

## Empirical transcript

### Before the improvement (commit `f51d477`)

Fixtures already rhymed: `peal nested.py:13 --exact` was only `return "denied"`; a `guards.rs:11` locator *scanned* the file and emitted span `11-12` (`let p` / `Some(p)`) even though rg only printed `let p`; `--hits` restored the ancestor line filter. `./peal` with no files exited 2 (`No cwd walk`). `--same-as` plus `rg -l` scanned the named file.

Real kizu told the truth about *which arm* once the file was known, and then the default pipe lied about *which file*.

```
$ cd kizu && rg -n 'let b_side' src/git/parse.rs | peal --explain
peal: LINE:text locators need a FILE operand, rg -nH, or FILE:LINE
# rc=2
```

Same footgun `when` / `ambit` had, and this mutation's own default (`rg | peal`) is exactly that pipe. Single-file rg omits the path. Passing `-nH` or a `FILE:LINE` locator already produced the invert of filtering:

```
$ printf '%s\n' "$KIZU/src/git/parse.rs:60" | ./peal --explain
seed    parse.rs:60
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];

deeper  parse.rs:61-62
  extra  if a_side!= b_side
  here   return None;

deeper  parse.rs:64
  extra  given a_side== b_side
  here   Some(bytes_to_path(a_side))
```

The quoted-form body is gone. `Some(bytes_to_path)` is in the scan; rg of `let b_side` never printed it. That is the flip, working, once the file is known.

`rg -nH 'return None;' parse.rs | peal` silently seeded the *first* return (quoted-form `:34`), not the unquoted survivor. Different lie, still open.

### After the improvement (this commit)

LINE:text locators are a partial image of a file. Matching `(line, text)` pins against git-listed sources (cwd / `--repo`) recovers the file if unique, then the first locator with a path-condition is the seed. Collapse still prefers a payload line over `{` / `}`.

```
$ cd kizu
$ rg -n 'let b_side' src/git/parse.rs | peal --explain
```

Same three spans as `parse.rs:60`, including `Some(bytes_to_path)`, without `-H` and without repeating the path. From the peal worktree, `--repo $KIZU` recovers the same file.

`peal parse.rs:54` (one given shallower) lists `:60` and `:64` as *deeper* — the same object approached from a prefix. `peal :60` does not list `:54`. That direction is the whole verb: superset, not subset.

```
$ ./peal fixtures/nested.py:10 --exact --explain
seed    fixtures/nested.py:10
  here   db.flush()
same    fixtures/nested.py:15
  here   return None
```

The `except` arm still is not.

`./demo.sh` exits 0 (26 tests + fixtures + kizu parse.rs:60 via `rg -n`).

## Dogfood targets

| target | what we asked |
| --- | --- |
| `kizu/src/git/parse.rs:60` | `rg -n 'let b_side'` → unquoted-form survivors; not quoted branch; not shallower `:54` |
| `kizu/src/git/parse.rs:54` | prefix: `:60`/`:64` appear as deeper |
| `kizu/src/git/parse.rs:25` | quoted-form exact arm |
| `fixtures/nested.py`, `guards.rs`, `sample.swift` | exact arm, stdin scan vs `--hits`, try≠except, guard≠guard-else |

Read-only on the real repos. Ugly fixtures live in `fixtures/`.

## Surprises

- The rhyme is unusable as `rg | tool` until locators name **files**. Filtering rg hits is a grep of lines that already mention something; the rest of the arm never will.
- Single-file rg omitting the filename is not a parser bug, it is the default. Recovering the file from `(line, text)` pins against `git ls-files` is the same object as the locators, not a walker: we never parse a file until uniqueness is known. Then the first pin with a non-empty cond_key is the seed.
- `--repo` is a *search root for pin recovery*, not a scan root. Passing kizu as a DIR operand still exits 2 without `--walk`.
- `rg -nH 'return None;'` is a bag of seeds, not one. First-locator seed is the quoted-form miss arm. The pipe that *works* for parse.rs:60 is a locator unique to that stack (`let b_side`), not "every early return in the function."

## Failures

1. **Inherited engine holes.** Nested-but-total early returns (quoted-path `if bytes.starts_with(b"\"a/") { … return Some }` is not `given ¬(quoted form)` at line 60), `if let` dropping `let`, `len<5+ 2` spacing, empty Rust match-arm preds — same as `when` / `chime`.
2. **First locator is the seed.** `rg 'return None;' parse.rs | peal` chimed the quoted-form arm (`:34`), not the unquoted survivor. No densest-arm / refuse-ambiguity yet. `--same-as parse.rs:60` overrides.
3. **Pin recovery needs a tree of names.** `rg /abs/parse.rs | peal` from another repo still fails unless `--repo` / FILE / `-nH`. We will not rglob the disk.
4. **Ambiguous pins.** Two files with the same text at the same line numbers → recovery refuses (exit 2), does not guess.
5. **`--diff` of an unapplied patch** maps `+` onto the working tree. Same hole as `when` / `chime`.
6. **Fallthrough `given` is statement-classed.** Python assignments after a guard do not carry the given; only subsequent `if`/`for`/`match` do. Inherited.
7. **Locator buffer.** The rg stream itself is collected (it is small). Scan/output is per named file.

## Suggested mutations

- When locators name several distinct cond_keys, refuse (ambiguous seed) unless `--first` / `--same-as`, or peal *each* unique stack.
- Overlay an unapplied patch so `--diff` is the post-image.
- Infer `given ¬(P)` for fully-exiting nested ifs (quoted-form miss on parse.rs) — then a `return None;` bag would not pick the quoted arm as if it chimed with the unquoted survivor.
- Cross-file rhyme: `rg -l` plus `--same-as` already scans named files; dogfood other parsers whose survivor stack is the same four givens (`--any-fn`).
- A TUI that paints every line of the recovered file same / deeper / other relative to the locator seed.

## Kill / keep

**Keep.** The object is the same as `chime`; the verb is now a Unix filter: `rg` picks files and (for `-n`) a seed locus, `peal` names the other lines those files run under the same (or a deeper) stack. Kill only if a later generation walks cwd again or reduces it to "print the grep hits that sit inside an `if`."
