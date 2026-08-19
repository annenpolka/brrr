# kith (hybrid-09)

v0.2. Leftovers of a change's **natal record**.

Leftovers of a change's **natal record**.

A natal record is a typed binding whose name inflects. Given a **commit or a diff** (never `FILE:LINE`), `kith` prints dest-tree lines that still speak that record: leftover *claims* (typed old values) and unpaid natal *kin* (inflected old names), fused at `path:line` as `via=claim|kin|both`.

`ember` leftover-matches claims a diff made false, but drops an unchanged value and does not case-fold a short natal (`t1` ↛ `T1`). `erst` leftover-matches unpaid kin, but truncates `0.3.0` to `0.3` and skips integer `10` as a common number. Concatenation is two lists. The object is one record; a dest line is one leftover.

`--no-fuse` is the concatenation the joint refuses.

## Install / run

Python 3.10+, `git` on `PATH`. No other deps.

```bash
chmod +x ./kith ./demo.sh
./kith self-test
./demo.sh
./kith --help
```

Exit `0` if the dest has no leftovers, `1` if any remain, `2` on usage/error.

```
kith HEAD                  # last commit vs HEAD leftovers
kith e9b0f75               # that change's natal record, still speaking at HEAD
kith A B                   # diff A→B, search B
git diff | kith --diff -   # stdin diff, search worktree
kith --json --check HEAD
```

## Examples

**1. Rename that did not move the number — leftover is via=both.**

`t1 = 15` → `driftDelay = 15`. Docs still say `T1 is 15 seconds.` Ember has no value fact (15 did not move) and does not fold `t1`→`T1`. Erst reports unpaid `T1` without typing `15` as a claim of this record.

```bash
./kith HEAD
# NATAL  t1↔driftDelay  15
#   both   docs/how to set (t1).md:3   T1 is 15 seconds.
```

**2. JSON version hunk — leftover is the full token.**

```bash
git diff -- plugin.json | ./kith --diff -
# NATAL  version  0.3.0 → 0.7.0
#   both   README.md:1   plugin version 0.3.0, hook timeout 10 seconds.
```

October is not leftover `10`. `DEBUG is True` is not leftover `ENABLE_CACHE`.

**3. sitbone hysteresis commit.**

```bash
./kith -C ~/src/sitbone e9b0f75
# NATAL  threshold↔presentThreshold  0.4 → 0.45
#   both   CLAUDE.md:329   @Test("… threshold 0.4")
#   both   docs/adr/0019-….md:76   `threshold: Double = 0.4`
```

`SiteObserver.threshold = 0.7` is a different domain.
