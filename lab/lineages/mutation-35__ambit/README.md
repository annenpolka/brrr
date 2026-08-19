# ambit

A Unix command nobody invented: **what runs in the ambit of this condition?**

`when` names a line and prints the path-condition. `under` inverted the query but still *walked a tree*. `ambit` keeps the invert and kills the walk.

Name a **predicate snippet**. Files come from **stdin locators** (`rg | ambit`) or explicit FILE operands. Every locus whose current path-condition contains the snippet is emitted — including fallthrough `given` frames from early-return guards, which never mention the condition on the surviving lines.

`rg` finds the token in source text. `ambit` finds the code that *runs only because that predicate is in force*. Piping `rg` does not filter to those lines; it **names the file to scan**.

## Install

```bash
chmod +x ./ambit
./ambit --help
```

Python 3.10+ (stdlib only). No extra packages. No cwd tree walk.

## Examples

```bash
# locators name the file; scan it (the rg hit need not be under the predicate)
rg -nH 'starts_with' fixtures/guards.rs | ./ambit 'starts_with(a/)' --explain

# rg -l is a file list
rg -l --type rust 'starts_with' kizu | ./ambit --kind given 'a/'

# single-file rg omits the filename: (line, text) pins recover it in this git tree
cd kizu && rg -n 'return None;' src/git/parse.rs | ./ambit --kind given 'a/' --explain
# still works with FILE / rg -nH / --repo if cwd is elsewhere

# explicit file, no pipe
./ambit 'user.locked' fixtures/nested.py --explain

# old under stdin-filter, if you really want only the grep hits
rg -n 'return' fixtures/nested.py | ./ambit 'user.locked' fixtures/nested.py --hits --tsv
```

### 1. Scan the file rg named, not the lines rg printed

```bash
printf '%s\n' 'fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {' \
  | ./ambit 'starts_with(a/)' --explain
```

Line 8 is the inverted `!starts_with` arm. `ambit` still emits `let p` — that line never contains `starts_with`, and rg did not print it. It runs *given* `bytes.starts_with(b"a/")`.

### 2. Guard fallthrough

```bash
./ambit 'isEnabled' fixtures/sample.swift --explain
```

The body after `guard isEnabled else { return }`, not the else.

### 3. Pipe a diff (still a line filter: the patch *is* the locators)

```bash
git diff -U0 | ./ambit 'isEnabled' --group
```

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human |
| `--tsv` | `file:span  n  side  depth  function  matched  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster by the matched predicate (buffers) |
| `--hits` | filter to stdin locator *lines* instead of scanning their files |
| `--walk` | opt-in DIR / cwd scan (the ancestor default, now off) |

Exit codes: `0` hits, `1` none, `2` usage, `3` not a git repo.

Default for a locator stream is TSV, flushed per file.

## Matching

- Snippets match the **path-condition stack**, not the line text.
- Spacing, quotes, and Rust `b"…"` prefixes fold away (`starts_with(a/)` hits `bytes.starts_with(b"a/")`).
- Identifier-boundary match: `unknownID` does not hit `unknownSelectionUnitID`.
- `A | B` is AND.
- Default polarity: `isEnabled` does not hit `guard-else`; `actual.has` does not hit `if (!actual.has)`.
- `--kind given|if|guard|…` restricts which frame may match.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
