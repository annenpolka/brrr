# same

Compare two local names under **exactly one** identity kind. The kind is required; the tool will not guess inode vs bytes vs JSON.

```
same --inode|--bytes|--json A B
```

origin:
  method: hdd
  trial: hdd-ident

## Primitive

Name the identity kind, then ask IDENTICAL or DISTINCT.

## Install / run

Python 3 stdlib only. From this worktree:

```bash
./same --inode A B
./demo.sh
python3 -m unittest tests.test_same -v
```

Exit: `0` identical, `2` distinct, `1` usage or parse error.

## Examples

Hard link, same inode:

```bash
./same --inode fixtures/hardlink/a fixtures/hardlink/b
# IDENTICAL inode 16777233:128975122
```

Two empty files, different inodes, same bytes:

```bash
./same --inode fixtures/empty/a fixtures/empty/b
# DISTINCT inode 16777233:128975119 16777233:128975120
./same --bytes fixtures/empty/a fixtures/empty/b
# IDENTICAL bytes sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

JSON key order is not identity under `--json`:

```bash
./same --json fixtures/json/order-ba.json fixtures/json/order-ab.json
# IDENTICAL json {"a":2,"b":1}
```

Omit the kind and the tool refuses:

```bash
./same fixtures/empty/a fixtures/empty/b
# usage: same --inode|--bytes|--json A B
# available kinds: inode, bytes, json
# exit 1
```

Missing files and non-UTF8 `--json` are path-named errors (exit 1), not tracebacks.
