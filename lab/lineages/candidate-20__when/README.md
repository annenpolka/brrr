# when

A Unix command nobody invented: **when does this line of code run?**

`grep` finds a line. `git blame` finds who last touched it. `git diff -W` shows the enclosing function. None of them answer the question a reviewer actually has about a changed line forty lines below an `if`:

> Under what conditions does this execute?

`when` prints the **path-condition stack** at a source locus — the nested `if` / `elif` / `try` / `except` / `match` / `guard` / `for` still in force, plus **`given` frames** for early-return guard clauses that already fired.

Unified diff context is line-based. `when` is condition-based.

## Install

```bash
chmod +x ./when
./when --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# one locus
./when fixtures/nested.py:13

# grep → when  (rg -nH, or: rg -n PAT FILE | ./when FILE)
rg -n 'return "denied"' fixtures | ./when --tsv

# annotate a patch with path-conditions, grouped
./when --diff fixtures/sample.diff --group

# annotate the working tree
./when --git --group
```

### 1. A return buried in nested if/try

```bash
./when fixtures/nested.py:13 --explain
```

```
fixtures/nested.py:13
  in     delete_user(user, db, audit)
  given  user is not None
  if     user.locked
  try
  if     user.role == 'admin'
  if     not user.can_delete
  here   return "denied"
```

### 2. Rust early-return fallthrough

```bash
./when fixtures/guards.rs:11 --explain
```

```
  in     parse_header(bytes: &[u8]) -> Option<usize>
  given  ¬(bytes.starts_with(b"\"a/"))
  given  ¬(bytes.len() < 7)
  given  bytes.starts_with(b"a/")
  here   let p = (bytes.len() - 5) / 2;
```

### 3. Pipe a diff, group by condition

```bash
git diff -U0 | ./when --group
```

Lines that run under the same predicates collapse into one bucket. Review the *conditions you changed*, not the hunk windows.

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default on a tty for a few loci) |
| `--tsv` | `file:line  side  depth  function  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster loci that share a path-condition |

Exit codes: `0` ok, `1` unresolved locus, `2` usage, `3` not a git repo.

## Engines

- **python-ast** — CPython AST: `if`/`elif`/`else`, `try`/`except`/`finally`, `for`/`for-else`, `match`/`case`, `with`, comprehensions, decorator lines, fallthrough `given`.
- **braces** — comment/string-aware scan for `.rs .go .js .ts .swift .java .c .cpp …`: `if`/`else if`, `match`/`switch`/`case`, Swift `guard`, simple-exit `given`.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
