# brood

From a **commit or a diff**, list every birth cohort that change still owes at HEAD.

Natal keys **inflect**. `t1` and `driftDelay` are one identity when the same line used to be named `t1`. `present_threshold` and `presentThreshold` are one identity by snake/camel. Renamed siblings still count as unpaid kin.

You do not point at `FILE:LINE`. The change is the query.

This is not `aka`. `aka` catalogs inflection pacts in a tree. `brood` only expands the natal keys of *this change's* birth cohort. `t1` ↔ `driftDelay` share no stem; they become one key because the line itself said `t1` at birth.

Reimplementation of `erst` (mutation-19) from observed CLI behavior only. The original source was never opened.

## Install / run

```bash
chmod +x ./brood
./brood --selftest
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

```bash
./brood                         # last commit vs HEAD
./brood HEAD~1                  # that commit's natal families, scored at HEAD
./brood e9b0f75
./brood main..HEAD              # a range (a PR)
./brood --wt                    # working tree vs HEAD
git diff | ./brood -
./brood --json --check HEAD
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / bad spec.

Passing `FILE:LINE` is an error. That is the point.

## Examples

A commit that renamed `t1` → `driftDelay` in one file and forgot the rest of its birth family:

```bash
./brood HEAD
# change commit  abcdef12  rename t1→driftDelay
#
# owing  4 unpaid  ·  b44d7853  introduce t1=15
# nee    t1↔driftDelay
# keys   t1
# delta  t1 → driftDelay
# paid   core.py:1: driftDelay = 15
# owing  tests/test_core.py:4: assert t1 == 15
#        (holds t1) since b44d785
# echo   docs/how to set (t1).md:3: T1 is 15 seconds.
```

`since` is occupancy of the leftover surface at HEAD (`git blame` of that line).

A commit that only bumped a number on the already-renamed line still finds the erstwhile name:

```bash
./brood <sha-that-bumped-driftDelay>
# keys include t1, because birth was `t1: TimeInterval = 15`
```

Snake/camel is the same identity without a historical rename:

```bash
# present_threshold → presentThreshold in one file
# leftover yaml `present_threshold:` is owing
```
