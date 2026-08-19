# brood

From a **commit or a diff**, list every birth cohort that change still owes at HEAD.

Natal keys **inflect**. `t1` and `driftDelay` are one identity when the same line used to be named `t1`. `present_threshold` and `presentThreshold` are one identity by snake/camel.

Natal **literals are domain-tagged**. `0.4` born as `threshold = 0.4` is `0.4@threshold`. A leftover `0.4` bound to `alpha` / `opacity` / `rgba` is a different brood, even if both numbers were introduced in the same commit.

You do not point at `FILE:LINE`. The change is the query.

This is not `aka`. `aka` catalogs inflection pacts in a tree. `brood` only expands the natal keys of *this change's* birth cohort.

This is not `also`. `also` wants `FILE:LINE`. Reviewers have a SHA.

This is not leftover-name search. A hit must share the natal domain, not merely the bytes.

Parent: `erst` (mutation-19). Flip: a natal literal is not a global token.

## Install / run

```bash
chmod +x ./brood
./brood --selftest
./demo.sh
```

Requires Python 3 and `git`. `--pr` also needs `gh`. No other dependencies.

```bash
./brood                         # last commit vs HEAD
./brood HEAD~1                  # that commit's natal families, scored at HEAD
./brood e9b0f75
./brood main..HEAD              # a range (a PR)
./brood --wt                    # working tree vs HEAD
git diff | ./brood -
./brood --pr                    # gh pr diff | brood -
./brood --json --tsv --check HEAD
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
# domain t1
# keys   t1@t1
# delta  t1 → driftDelay
# paid   core.py:1: driftDelay = 15
# owing  tests/test_core.py:4: assert t1 == 15
# echo   docs/how to set (t1).md:3: T1 is 15 seconds.
```

A commit that bumped a **threshold** `0.4` → `0.45` does not accuse a same-byte **opacity** leftover:

```bash
./brood HEAD
# keys   0.4@present_threshold
# owing  tests/test_core.py:5: assert present_threshold == 0.4
# (ui/overlay.py `alpha = 0.4` is silent — different domain)
```

`erst` on the same fixture lists `alpha = 0.4` as unpaid kin. `brood` does not.

Snake/camel is the same identity without a historical rename:

```bash
# present_threshold → presentThreshold in one file
# leftover yaml `present_threshold: 0.4` is owing
# leftover `opacity(0.4)` is not
```
