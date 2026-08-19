# winnow

Partition an uncommitted working tree into **wheat** (the smallest change set that reproduces a command's current behavior) and **chaff** (everything else).

This is `git bisect` for the dirty diff, not for commits.

## Install / run

Needs Python 3.9+ and `git`. No other dependencies.

```bash
chmod +x winnow
./winnow -- pytest tests/test_foo.py
# or:
python3 ./winnow --format paths -- pytest tests/test_foo.py
```

`./demo.sh` builds throwaway git repos and checks isolation. It must exit 0.

## Examples

**1. Which of these WIP files actually broke the test?**

```bash
./winnow --format text -- python3 test.py
```

```
HEAD: exit=0 pass
WIP:  exit=1 AssertionError
wheat (1/4):
  modify app.py
chaff (3/4):
  modify README.md
  modify helper.py
  add    notes.txt
```

**2. Paths only, for pipelines**

```bash
./winnow --format paths -- python3 test.py
# app.py
```

**3. Wheat as a patch**

```bash
./winnow --format patch -- python3 test.py > guilty.patch
```

The working tree is restored after the run (including on SIGINT). The git index is never touched.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` | git repo (and command cwd) |
| `--cwd DIR` | command cwd only |
| `--base REF` | baseline (default `HEAD`) |
| `--format text\|paths\|json\|patch` | output |
| `--fingerprint all\|stderr\|exit\|raw` | what "same behavior" means |
| `-v` | print each trial |

Exit 0 on a successful partition (including "WIP does not affect this command"). Exit 2 for usage/tool errors. Exit 3 if the command is flaky.
