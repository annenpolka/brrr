# amid

A Unix command nobody invented: **`rg` names the file; the condition names the lines.**

`under` walks a tree looking for a predicate. `amid` is the stream flip: pipe locators (`rg | amid PRED`), scan **the same file those locators came from**, emit every locus whose path-condition contains the predicate — including fallthrough `given` frames that never mention it.

`rg` finds a mention. `amid` expands that mention to the rest of the file that *runs only because the condition is in force*.

## Install

```bash
chmod +x ./amid
./amid --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# rg hit is line 13; amid also prints the rest of the locked arm
printf 'fixtures/nested.py:13:    return "denied"\n' | ./amid 'user.locked' --explain

# single-file rg omits the filename — pass the FILE once
rg -n 'return' fixtures/nested.py | ./amid 'user.locked' fixtures/nested.py --tsv

# rust: pipe the early-return if, get the surviving given
printf 'fixtures/guards.rs:8:    if !bytes.starts_with(b"a/") {\n' \
  | ./amid 'starts_with(a/)' --explain

# heading stream (rg --heading)
rg --heading -n 'isEnabled' fixtures/sample.swift | ./amid 'isEnabled'

# rg --json always carries the file; omit the snippet and the locator names it
rg --json 'starts_with' fixtures/guards.rs | ./amid --explain

# keep only the piped lines (the old under filter)
rg -nH 'return' fixtures/nested.py | ./amid 'user.locked' --pin --tsv
```

### 1. Locators name the file, not the answer

```bash
printf 'fixtures/nested.py:13:    return "denied"\n' | ./amid 'user.locked' --explain
```

Line 13 is what `rg` knew. `amid` scans that same file and also reports the other lines that run under `user.locked` (`db.flush()`, the admin arm). The drained-queue return is not in this file-region of the condition.

### 2. Guard fallthrough from an if-line locator

```bash
printf 'fixtures/guards.rs:8:    if !bytes.starts_with(b"a/") {\n' \
  | ./amid 'starts_with(a/)' --explain
```

The piped line is the *evaluating* `if !starts_with`. The hit is `Some(p)` — the survivor of the early return — which `rg starts_with` never printed.

### 3. No tree walk

```bash
./amid 'user.locked'            # usage error (stdin empty, no FILE)
./amid 'user.locked' fixtures/  # usage error unless --tree
./amid 'user.locked' fixtures/nested.py   # explicit file, ok
```

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human |
| `--tsv` | default on a stream: `file:span  n  side  depth  function  matched  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster by the matched predicate (buffers) |
| `--pin` | filter the locators instead of scanning their files |
| `--tree` | walk a named directory (opt-in) |

Exit codes: `0` hits, `1` none, `2` usage, `3` not a git repo.

Hits are written as each new file appears on stdin (streamed). `--group` is the exception.

## Matching

Same object as `under` / `when`: the **path-condition stack**, not the line text.

- Spacing, quotes, and Rust `b"…"` prefixes fold away (`starts_with(a/)` hits `bytes.starts_with(b"a/")`).
- Identifier-boundary match: `unknownID` does not hit `unknownSelectionUnitID`.
- `A | B` is AND.
- Default polarity: `isEnabled` does not hit `guard-else`; `starts_with(a/)` does not hit `if !starts_with`.
- `--kind given|if|guard|…` restricts which frame may match.
- No snippet: each locator's `if`/`guard` pred is the snippet. A leading `!`/`¬` on that if-line is peeled so the question is the fallthrough given.
- `rg --json` always includes the path, even for a single file.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
