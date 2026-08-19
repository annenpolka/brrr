# erst

From a **commit or a diff**, list every birth cohort that change still owes at HEAD.

Natal keys **inflect**. `t1` and `driftDelay` are one identity when the same line used to be named `t1`. `present_threshold` and `presentThreshold` are one identity by snake/camel. Renamed siblings still count as unpaid kin.

You do not point at `FILE:LINE`. The change is the query.

This is not `aka`. `aka` catalogs inflection pacts in a tree. `erst` only expands the natal keys of *this change's* birth cohort. `t1` ↔ `driftDelay` share no stem; they become one key because the line itself said `t1` at birth.

## Install / run

```bash
chmod +x ./erst
./erst --selftest
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

```bash
./erst                         # last commit vs HEAD
./erst HEAD~1                  # that commit's natal families, scored at HEAD
./erst e9b0f75
./erst main..HEAD              # a range (a PR)
./erst --wt                    # working tree vs HEAD
git diff | ./erst -
./erst --json --check HEAD
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / bad spec.

Passing `FILE:LINE` is an error. That is the point.

## Examples

A commit that renamed `t1` → `driftDelay` in one file and forgot the rest of its birth family:

```bash
./erst HEAD
# change commit  abcdef12  rename t1→driftDelay
#
# owing  4 unpaid  ·  b44d7853  introduce t1=15
# nee    t1↔driftDelay
# keys   t1
# delta  t1 → driftDelay
# paid   core.py:1: driftDelay = 15
# owing  tests/test_core.py:4: assert t1 == 15
# echo   docs/how to set (t1).md:3: T1 is 15 seconds.
```

A commit that only bumped a number on the already-renamed line still finds the erstwhile name:

```bash
./erst <sha-that-bumped-driftDelay>
# keys include t1, because birth was `t1: TimeInterval = 15`
```

Snake/camel is the same identity without a historical rename:

```bash
# present_threshold → presentThreshold in one file
# leftover yaml `present_threshold:` is owing
```
