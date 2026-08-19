# skew

Show the definition-diff a *caller file* has not been saved or committed through.

The clock is **file mtime when the worktree differs from HEAD**, otherwise the **last commit that touched the file** — not `git blame`, not per-line history. Coarser than line-blame join, still answers: has this callee changed since this caller file was last saved/committed?

## Install / run

```bash
chmod +x skew demo.sh
./skew --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Point `--repo` at any git checkout, or run from inside one.

```bash
./skew [--repo PATH] [--diff] [--sig] [--dirty] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Exit 0 on a successful query. `--check` exits 1 if any skewed caller file is found (CI). Unscoped runs hide "ghosts" (the name did not exist yet at the caller file's clock); pass `--ghosts` or a symbol to include them.

`--dirty` keeps only callees whose clock is worktree mtime — the pre-commit view of HEAD vs worktree.

## Examples

**1. Which files slept through a function change?**

```bash
./skew --repo ./fixtures/lagrepo --diff greet
```

Prints `src/app.py`, `tests/test_greet.py`, and `docs/api.md` as *files* whose last commit is older than `src/greet.py`'s, plus the unified diff those files have never been saved through. `src/cli.py` still sleeps through the later `prefix=` change (its file clock is in between). Two mentions in `app.py` collapse to one file row.

**2. Dirty callee: mtime beats last-commit.**

```bash
# after editing src/greet.py without committing
./skew --repo ./fixtures/lagrepo --diff --dirty greet
```

`src/fresh.py` was committed in the same commit as the last `greet` change, so a committed-only clock says it is current. Once `greet.py` is dirty, its clock is mtime/WORKTREE and `fresh.py` lags — the HEAD vs worktree case blame never saw.

**3. Pin a file (or a line's tokens) and pipe.**

```bash
./skew --repo ~/src/kizu --format tsv --sig src/app.rs \
  | awk -F'\t' 'NR>1 {print $1, $10, $4"d", $8}' \
  | sort -u
```

`path:line` still selects which tokens on that line to join; the clock remains the file's.
