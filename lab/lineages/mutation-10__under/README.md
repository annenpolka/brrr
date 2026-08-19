# under

A Unix command nobody invented: **where does this condition hold?**

`when` names a line and prints the path-condition. `under` is the reverse: name a **predicate snippet**, get every locus whose current path-condition contains it.

`rg` finds the token in source text. `under` finds the code that *runs only because that predicate is in force* — including fallthrough `given` frames from early-return guards, which never mention the condition on the surviving lines.

## Install

```bash
chmod +x ./under
./under --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# every line that runs under user.locked
./under 'user.locked' fixtures/nested.py

# AND of two conditions (a path-condition fragment)
./under 'user.locked | can_delete' fixtures/nested.py --explain

# rust: lines that survived the a/ prefix check
./under 'starts_with(a/)' fixtures/guards.rs --kind given

# swift: after the isEnabled guard, not the guard-else
./under 'isEnabled' fixtures/sample.swift

# keep only grep hits that actually run under the condition
rg -n 'return' fixtures/nested.py | ./under 'user.locked' fixtures/nested.py --tsv

# filter a patch to the arm you care about
./under 'can_delete' --diff fixtures/sample.diff --group
```

### 1. One condition, every locus

```bash
./under 'user.locked' fixtures/nested.py --explain
```

```
fixtures/nested.py:13
  match  if user.locked
  in     delete_user(user, db, audit)
  given  user is not None
  if     user.locked          ←
  try
  if     user.role == 'admin'
  if     not user.can_delete
  here   return "denied"
```

The `if user.locked:` line itself is not listed (it is still *evaluating* the test). The denied return is. The drained-queue return is not.

### 2. Guard fallthrough, by kind

```bash
./under 'user is not None' --kind given fixtures/nested.py --tsv
```

Everything after `if user is None: return` — the condition no longer appears in the source of those lines.

### 3. Pipe a diff

```bash
git diff -U0 | ./under 'isEnabled' --group
```

Only the hunks that execute under that predicate.

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default on a tty for a few hits) |
| `--tsv` | `file:span  n  side  depth  function  matched  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster by the matched predicate, then remaining stack |

Exit codes: `0` hits, `1` none, `2` usage, `3` not a git repo.

## Matching

- Snippets match the **path-condition stack**, not the line text.
- Spacing, quotes, and Rust `b"…"` prefixes fold away (`starts_with(a/)` hits `bytes.starts_with(b"a/")`).
- Identifier-boundary match: `unknownID` does not hit `unknownSelectionUnitID`; `Decision:` does not hit `decision_section`.
- `A | B` is AND.
- Default polarity: `isEnabled` does not hit `guard-else`; `len<7` does not hit `given ¬(len<7)`; `actual.has` does not hit `if (!actual.has)`. Use `--kind given` or write the `¬` / `!` to ask for the inversion.
- `--kind given|if|guard|…` restricts which frame may match.
- `--eval` also matches the evaluating `if` line.
- `--same-as FILE:LINE` uses that locus's in-force conditions as the snippet.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
