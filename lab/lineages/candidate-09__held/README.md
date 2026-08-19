# held

Intervals of git history where a predicate holds — the missing partner of `git bisect`.

## Install / run

```bash
# from this directory
./held --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `held` onto your `PATH` if you want.

Exit codes: `0` predicate holds at the last sample (HEAD, or the working tree with `--now`), `1` it does not, `2` tool error.

## Examples

**1. When did this file exist?** (`git log -- PATH` lies for deleted files.)

```bash
held --full exists Sources/SitboneUI/FocusRiverView.swift
```

```
FALSE  11 commits  a2512fe..74363dc
TRUE   11 commits  14b1d6e..1fefafb  2026-03-31 → 2026-04-01
FALSE  78 commits  70ec7df..094769d
```

**2. When did this string inhabit the tree?** (not when it *changed* — that is `git log -S`.)

```bash
held grep circuit-breaker
```

```
FALSE  15 commits  9adb747..5317362  2025-12-19 → 2026-04-07
TRUE    6 commits  11716a3..e0ad330  2026-04-07
FALSE  28 commits  2d56b11..6b19433  2026-04-07 → 2026-07-25
```

**3. Arbitrary predicate, including dirty-tree as a final sample.**

```bash
held exec -- test -f Makefile
held --now exists src/foo.rs
held --json grep -i TODO -- src | jq '.eras[] | select(.value)'
```

Pipe the true interval into git:

```bash
held --true-bounds exists .github/workflows/ci.yml |
  while read start end value count; do git log --oneline "$start^..$end"; done
```

Default walk is **first-parent** (eras of mainline). The header prints `24 of 244 commits` when that walk hides reachable history. Use `--full` for every reachable commit — needed when a path lived only on a topic branch that merged with the file already gone.

If a query never holds, `held` diagnoses the usual footguns: a stray unquoted word treated as a pathspec, case (`-i`), or occupancy only off the mainline (`--full`).
