# unseen

Show the definition-diff a use-site has never seen: the callee as it was when that line was last touched, versus now.

## Install / run

```bash
chmod +x unseen demo.sh
./unseen --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Point `--repo` at any git checkout, or run from inside one.

```bash
./unseen [--repo PATH] [--diff] [--sig] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Exit 0 on a successful query. `--check` exits 1 if any sleeping use-site is found (CI). Unscoped runs hide "ghosts" (the name did not exist yet at that use-site); pass `--ghosts` or a symbol to include them.

## Examples

**1. What did callers miss after a function changed?**

```bash
./unseen --repo ./fixtures/lagrepo --diff greet
```

Prints `src/app.py`, `tests/test_greet.py`, and `docs/api.md` as use-sites that last moved before `greet` gained `excited` and `prefix`, plus the unified diff they have never seen.

**2. Pin one line (editor / bisect workflow).**

```bash
./unseen --repo ./fixtures/lagrepo --diff src/app.py:5
```

For the tokens on that line, emit only the definition changes that line has not been edited through.

**3. Pipe into other Unix tools.**

```bash
./unseen --repo ~/src/kizu --format tsv --sig \
  | awk -F'\t' 'NR>1 {print $1, $9":"$10, $4"d"}' \
  | sort -u
```
