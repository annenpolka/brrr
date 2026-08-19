# lien (mutation-57)

v0.2. CI gate on leftovers of a change's **natal record**.

A natal record is a typed binding whose name inflects. Default input is a **unified diff on stdin**. Default output is **`--check`**: one dest-line lien (`path:line: via: …`), silent on success, exit 1 if the dest tree still speaks that record. `--explain` is the human natal dump.

Ancestor `kith` dumps first and takes a SHA. `lien` is not a flag on kith. Ember leftover-matches claims a diff made false, but drops an unchanged value and does not case-fold a short natal (`t1` ↛ `T1`). Erst leftover-matches unpaid kin, but truncates `0.3.0` to `0.3` and skips integer `10`. Concatenation is two lists. The object is one record; a dest line is one leftover; CI sees the dest line.

## Install / run

Python 3.10+, `git` on `PATH`. No other deps.

```bash
chmod +x ./lien ./demo.sh
./lien self-test
./demo.sh                 # exits 0; fixture + sitbone e9b0f75 both-rows
./lien --help
```

Exit `0` if the dest has no leftovers, `1` if any remain, `2` on usage/error.

```
git diff | ./lien                     # CI check (default): current liens
git diff origin/main...HEAD | ./lien  # PR gate
git diff | ./lien --explain           # human natal dump (union)
git diff | ./lien --all               # CI-print kin + migration docs too
./lien --explain -C <repo> e9b0f75    # opt-in SHA dump
git diff | ./lien --json
git diff | ./lien -q                  # exit code only
```

`FILE:LINE` exits 2. Garbage stdin that is not a unified diff exits 2.

## Examples

**1. Rename that did not move the number — CI lien is via=both.**

`t1 = 15` → `driftDelay = 15`. Docs still say `T1 is 15 seconds.`

```bash
git diff HEAD^ HEAD | ./lien
# docs/how to set (t1).md:3: both: t1↔driftDelay  15: T1 is 15 seconds.
echo $?   # 1
```

`--explain` groups that leftover under the natal record.

**2. JSON version hunk — leftover is the full token.**

```bash
git diff -- plugin.json | ./lien
# README.md:1: both: version  0.3.0 → 0.7.0: plugin version 0.3.0, hook timeout 10 seconds.
```

October is not leftover `10`. `DEBUG is True` is not leftover `ENABLE_CACHE`.

**3. sitbone hysteresis commit — both-rows fail the gate.**

```bash
git -C ~/src/sitbone diff e9b0f75^ e9b0f75 | ./lien -C ~/src/sitbone
# CLAUDE.md:329: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
# CLAUDE.md:332: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
```

`SiteObserver.threshold = 0.7` is a different domain. `SPEC.md` `v0.4` is not leftover float `0.4`. Kin-only ADR quotes are `--explain`, not a CI fail.
