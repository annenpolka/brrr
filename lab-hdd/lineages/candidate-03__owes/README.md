# owes

List obligations a working-tree change appears to break.

`git diff` shows what moved. `owes` asks whether remaining docs and tests
still require something the change removed, or name a companion file that
is not in the remaining tree.

```yaml
origin:
  method: hdd
  trial: hdd-agent
```

## Install

Python 3 stdlib only. The shipped CLI is `./owes`.

```bash
chmod +x owes
```

## Usage

```text
owes DIR
owes --tree TREE --diff DIFF
owes --json DIR
```

`DIR` is a snapshot of the change, in one of two layouts:

- `DIR/change.diff` plus remaining files in `DIR/tree`
- `DIR/before` and `DIR/after` (diff is computed; remaining tree is `after`)

`--tree TREE --diff DIFF` is the same core: parse the unified diff, search
the remaining tree.

Exit codes: `0` none unkept, `2` unkept obligation, `1` usage error.

## What it reports

1. **Unkept references** — function/class/const-looking names on diff minus
   lines that still appear in remaining files. Mentions whose line text was
   introduced on a plus line of the same change (a changelog "Removed foo")
   are skipped.
2. **Missing companions** — remaining `*.md` files that say `MUST exist: PATH`
   or `required file: PATH`, or a filename-like backtick path after "must",
   when `PATH` is not in the remaining tree. Shell commands such as
   `must run \`make test\`` are not treated as files.

## Demo

```bash
./demo.sh
```

Three fixtures:

1. `validate_input` deleted, still mentioned in `README.md` → exit 2
2. remaining doc says `MUST exist: SECURITY.decision.md` and that file is
   absent → exit 2
3. unused helper deleted, required file present → exit 0

## Tests

Tests call the shipped CLI, not imported internals:

```bash
python3 tests/test_owes.py -v
```
