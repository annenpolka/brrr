# owe

From a **commit or a diff**, list every birth cohort in that change that is already unpaid at HEAD.

You do not point at `FILE:LINE`. The change is the query: natal siblings introduced together, then left behind.

## Install / run

```bash
chmod +x ./owe
./owe --selftest
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

```bash
./owe                         # last commit vs HEAD
./owe HEAD~1                  # that commit's natal families, scored at HEAD
./owe abc123
./owe main..HEAD              # a range (a PR)
./owe --wt                    # working tree vs HEAD
git diff | ./owe -
./owe --json --check HEAD
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / bad spec.

Passing `FILE:LINE` is an error. That is the point.

## Examples

A commit that bumped one constant and forgot the rest of its birth family:

```bash
./owe HEAD
# change commit  abcdef12  raise TIMEOUT to 60
#
# owing  5 unpaid  ·  b44d7853  introduce timeout=30
# keys   30
# delta  30 → 60
# paid   config.py:1: TIMEOUT = 60
# owing  tests/test_timeout.py:4: assert TIMEOUT == 30
# owing  docs/how to set (timeout).md:3: The service timeout is 30 seconds.
```

Ask the introducing commit whether that family later split:

```bash
./owe HEAD~1
# split  2 factions  ·  b44d7853  introduce timeout=30
#        HEAD 30×5  60×1
```

The working tree, same question — no line number required:

```bash
git diff | ./owe -
```
