# sire (mutation-68)

v0.2. Given a leftover `FILE:LINE`, show the change whose **natal record** that line still speaks.

lien asks whether a *diff* leaves dest lines that still speak the natal. `sire` inverts: the input is a locator, the output is the natal commit + old→new + via=claim|kin|both.

Not `git blame` (who last touched the line). Not ember (leftover-matches a *given* diff). Not a leftover-name walker.

## Install / run

Python 3.10+, `git` on `PATH`. No other deps.

```bash
chmod +x ./sire ./demo.sh
./sire self-test
./demo.sh                 # exits 0; fixture + sitbone CLAUDE.md:329
./sire --help
```

Exit `0` if a sire is found, `1` if the locator speaks no natal change, `2` on usage/error.

```
./sire CLAUDE.md:329
./sire -C <repo> CLAUDE.md:329
printf 'CLAUDE.md:329\n' | ./sire -C <repo>
git diff | lien | ./sire          # locators, not the diff
./sire --explain CLAUDE.md:329
./sire --json docs/how\ to\ set\ \(t1\).md:3
```

A unified diff on stdin exits 2. `HEAD` is not a locator.

## Examples

**1. Leftover test claim → hysteresis commit, not git blame.**

sitbone `CLAUDE.md:329` still says `threshold 0.4`. `git blame` names `a2512fe` (initial design docs). The natal change is `e9b0f75` (`threshold`/`0.4` → `presentThreshold`/`0.45`).

```bash
./sire -C ~/src/sitbone CLAUDE.md:329
# CLAUDE.md:329: e9b0f75: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4")
```

`SPEC.md:436` `v0.4  カメラPresence検出` is not leftover float `0.4` (exit 1).

**2. Unmoved value, inflected name.**

`t1 = 15` → `driftDelay = 15`. Docs still say `T1 is 15 seconds.` Pickaxe `-S 15` cannot see it. `sire` inflects `T1` → `t1`.

```bash
./sire -C "$FIX" "docs/how to set (t1).md:3"
# docs/how to set (t1).md:3: <sha>: both: t1↔driftDelay  15: T1 is 15 seconds.
```

**3. Kin-only ADR quote, and lien dest-lines as stdin.**

```bash
./sire --explain -C ~/src/sitbone docs/adr/0019-presence-hysteresis.md:12
# via=kin  e9b0f75  threshold↔presentThreshold  0.4 → 0.45

echo 'docs/how to set (t1).md:4: both: …' | ./sire -C "$FIX"
```

October is not leftover `10`. Paid `driftDelay = 15` is not a leftover.
