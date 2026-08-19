# also

Show the birth-siblings of a source line — what was introduced in the same commit, sharing its distinctive tokens — and whether those siblings have drifted.

## Install / run

```bash
chmod +x ./also
./also --selftest
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

```bash
./also FILE:LINE
./also -C /path/to/repo FILE:LINE
./also --json --check FILE:LINE
git diff | ./also --diff -
```

Exit codes: `0` ok, `1` `--check` found drift, `2` usage / not a repo / bad location.

## Examples

Point at a constant whose value moved. `also` walks `git log -L` to the introducing commit, treats other added lines that shared its literals as kin, echoes current copies of those literals (even unique strings added later), and reports which of those lines still agree.

```bash
./also -C ~/src/service config.py:1
# query  config.py:1
#        TIMEOUT = 60
# birth  b44d78531784  introduce timeout=30 and retry=3
#        was: TIMEOUT = 30
# keys   timeout, 30
#
# drift  docs/how to set (timeout).md:3: The service timeout is 30 seconds.
#        (query lost 30)
# drift  tests/test_timeout.py:4: assert TIMEOUT == 30
```

Ask the working tree the same question: *you changed this literal; what unpaid kin remains?*

```bash
git diff | ./also --diff -
```

Machine-readable report for one location, failing CI if kin drifted:

```bash
./also --json --check src/timeout.py:1 > /tmp/also.json
```
