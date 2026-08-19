# berth

From a **commit or a diff**, list every birth cohort that change still owes at HEAD.

Natal keys **inflect**. `t1` and `driftDelay` are one identity when the same line used to be named `t1`. Leftover occupancy `since` is the leftover **identity birth** (the rename that made the mention unpaid, or a later intro of that identity on the path) — not `git blame` last-touch of the leftover line.

You do not point at `FILE:LINE`. The change is the query.

This is not `brood`. `brood` blames the leftover hunk (`T1` on SPEC.md → `a2512fe`, a docs rewrite / root touch). `berth` follows the unpaid identity: that same leftover berths at the rename (`1fcdec6`) because `T1` was already sitting there when `t1` became `driftDelay`. A formatter that rewrites the line without changing the identity count is ignored.

Mutation-56 of `erst`/`brood`. Isolated tool; the ancestor was not edited.

## Install / run

```bash
chmod +x ./berth
./berth --selftest
./demo.sh
```

Requires Python 3 and `git`. No other dependencies.

```bash
./berth                         # last commit vs HEAD
./berth HEAD~1                  # that commit's natal families, scored at HEAD
./berth e9b0f75
./berth 1fcdec6
./berth main..HEAD              # a range (a PR)
./berth --wt                    # working tree vs HEAD
git diff | ./berth -
./berth --json --check HEAD
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / bad spec.

Passing `FILE:LINE` is an error. That is the point.

## Examples

A commit that renamed `t1` → `driftDelay` in one file and forgot the rest of its birth family. Docs were rewritten after `T1` was introduced; last-touch is the rewrite. Occupancy is the rename:

```bash
./berth HEAD
# change commit  abcdef12  rename t1→driftDelay
#
# owing  4 unpaid  ·  b44d7853  introduce t1=15
# nee    t1↔driftDelay
# keys   t1
# delta  t1 → driftDelay
# paid   core.py:1: driftDelay = 15
# owing  tests/test_core.py:4: assert t1 == 15
#        (holds t1) since abcdef1
# owing  docs/how to set (t1).md:3: T1 is 15 seconds.
#        (holds T1) since abcdef1 born b44d785
```

sitbone lint rename `1fcdec6`. Leftover `T1` on SPEC.md last-touched `a2512fe`. Occupancy `since` is the rename; `born` is when that path first held the identity:

```bash
./berth -C /path/to/sitbone 1fcdec6
# owing  SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
#        (holds T1) since 1fcdec6 born a2512fe
```

A commit that only bumped a number on the already-renamed line still finds the erstwhile name:

```bash
./berth <sha-that-bumped-driftDelay>
# keys include t1, because birth was `t1: TimeInterval = 15`
```
