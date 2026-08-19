# whence

A Unix command rebuilt from the observed behavior of `when(1)`: **whence does this line of code run?**

`grep` finds a line. `git blame` finds who last touched it. `git diff -W` shows the enclosing function. None of them answer the question a reviewer actually has about a changed line forty lines below an `if`:

> Under what conditions does this execute?

`whence` prints the **path-condition stack** at a source locus — the nested `if` / `elif` / `try` / `except` / `match` / `guard` / `for` still in force, plus **`given` frames** for early-return guard clauses that already fired.

This is a Generation-2 reimplementation (`reimpl-04`). The original Python was never opened. CLI shape, fixtures, and the kizu `parse.rs:60` four-given stack were recovered by running the original binary.

## Install

```bash
chmod +x ./whence
./whence --help
```

Python 3.10+ (stdlib only). No extra packages.

## Examples

```bash
# one locus
./whence fixtures/nested.py:13

# grep → whence  (rg -nH, or: rg -n PAT FILE | ./whence FILE)
rg -n 'return "denied"' fixtures | ./whence --tsv

# annotate a patch with path-conditions, grouped
./whence --diff fixtures/sample.diff --group

# the gold stack: four fallthrough givens on real Rust
./whence /path/to/kizu/src/git/parse.rs:60 --explain
```

### 1. A return buried in nested if/try

```bash
./whence fixtures/nested.py:13 --explain
```

```
fixtures/nested.py:13
  in     delete_user(user, db, audit)
  given  user is not None  (L5)
  if     user.locked  (L8)
  try      (L9)
  if     user.role == 'admin'  (L11)
  if     not user.can_delete  (L12)
  here   return "denied"
```

### 2. Rust early-return fallthrough

```bash
./whence fixtures/guards.rs:11 --explain
```

```
  in     parse_header(bytes: &[u8]) -> Option<usize>
  given  ¬(bytes.starts_with(b"\"a/"))
  given  ¬(bytes.len()<7)
  given  bytes.starts_with(b"a/")
  here   let p = (bytes.len() - 5) / 2;
```

### 3. kizu parse.rs:60 — four givens

```bash
./whence kizu/src/git/parse.rs:60 --explain
```

```
  in     parse_diff_git_header(rest:&str)-> Option<PathBuf>
  given  ¬(len<5+ 2)
  given  inner.is_multiple_of(2)
  given  bytes.starts_with(b"a/")
  given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")
  here   let b_side = &bytes[b_prefix_start + 3..];
```

## Output

| flag | meaning |
| --- | --- |
| `--explain` | multi-line human (default on a tty for a few loci) |
| `--tsv` | `file:line  side  depth  function  path  source  engine` |
| `--json` | NDJSON records |
| `--group` | cluster loci that share a path-condition |

Exit codes: `0` ok, `1` unresolved locus, `2` usage, `3` not a git repo.

See `CANDIDATE.md` for the primitive, dogfood transcript, and failures.
