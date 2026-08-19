# doze

Show use-sites that last saw a **different signature** than HEAD.

Default output is signature changes only. `--check` is the CI verb: exit 1 if any use-site last saw a different signature than HEAD. Body-only diffs sit behind `--body`. Ghost English-word ranking is gone. Last-saw vs HEAD headers are whitespace-collapsed, so a multiline reflow is not a contract change.

## Install / run

```bash
chmod +x doze demo.sh
./doze --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Point `--repo` at any git checkout, or run from inside one.

```bash
./doze [--repo PATH] [--check] [--body] [--diff] [--ghosts] [--format human|json|tsv] [symbol|path|path:line]
```

Exit 0 on a successful query with no signature lag. `--check` exits 1 if any use-site last saw a different signature than HEAD.

## Examples

**1. What signature did callers miss?**

```bash
./doze --repo ./fixtures/lagrepo greet
```

Prints `src/app.py`, `tests/test_greet.py`, and `docs/api.md` as use-sites that last moved before `greet` gained `excited` and `prefix`, plus the last-saw vs HEAD signatures. Body-only `trim` is hidden.

**2. CI gate.**

```bash
./doze --check --repo . insert_scar
```

Exit 1 and print `path:line: insert_scar: signature changed` with last-saw / HEAD headers if any use-site still sees the old contract. Silent exit 0 if every use-site last saw the HEAD signature.

**3. Pin one line, or include body diffs.**

```bash
./doze --repo ./fixtures/lagrepo src/app.py:5
./doze --repo ./fixtures/lagrepo --body --format tsv \
  | awk -F'\t' 'NR>1 && $3=="0" {print $1, $9":"$10}'
```
