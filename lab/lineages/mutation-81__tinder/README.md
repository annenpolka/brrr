# tinder (mutation-81)

Leftover **claim** in, fact-falsifying **commit** out. Dest-file identity **follows**.

smolder inverts leftover: dest locus in, falsifying commit/hunk out (ash = regenerate). Hole: a leftover that **moved with a dest-file rename** still names the rename (`git log -S leftover -- dest/newpath`), not the commit that falsified the fact.

**tinder** `--follow`s the leftover across dest-file identity (berth/slip). Query the old name or the new name. Name the commit that mutated the **fact**. A dest-only rename is not a falsifier. Copy is not follow (R records, not `git log --follow` blob walk). Dest leftover is a typed claim, not leftover-name.

A *fact* is a typed bound name/value, rename, or polarity flip. Regenerated dest (`generated/`, `oracle/`, lockfile, `*.generated.*`, `@generated` banner) is **ash**: leftover *build*. Ash answers **regenerate**, never "edit this line". October is not timeout 10.

Not leftover names (haunt / wraith). `FILE:LINE` is legal **input**.

## Install / run

Python 3.9+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./tinder ./demo.sh
./tinder self-test
./demo.sh                 # fixtures + gold kizu/sitbone/tenaoshi if present; exits 0
./tinder --help
```

Exit codes: `0` found (falsifier or regenerate), `1` none, `2` usage/error.

```bash
./tinder -C <repo> path/to/file:LINE
./tinder -C <repo> old-name.md:7          # follows dest identity to the live holder
./tinder --no-follow -C <repo> old-name.md:7   # path is identity; dead name is missing
printf 'README.md:7\n' | ./tinder -C <repo>
git diff A B | ./tinder --diff - -C <repo> leftover.md:3
```

## Examples

**1. Leftover moved with a dest-file rename — name the fact, not the rename.**

```bash
./tinder --no-color -C sitbone CLAUDE.md:329
```

```
tinder: leftover  CLAUDE.md:329

CLAIM @Test("… threshold 0.4）")
  CLAUDE.md:329

FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

After `git mv docs/help.md docs/guide.md`, `docs/guide.md:1` and the dead `docs/help.md:1` both name the timeout bump. `git log -S 10 -- docs/guide.md` names the rename. tinder does not.

kizu's dest leftover *moved* into `docs/` (`4e37f16`). The dead name still follows. Path-limited pickaxe names the rename. The leftover still claims `"timeout": 10`, which is still true of the installer — tinder says **none**, not a quote tweak in `init.test.ts`.

**2. A generated lockfile leftover is ash — regenerate, do not blame a comment.**

```bash
./tinder --no-color -C kizu Cargo.lock:168
```

```
tinder: ash  Cargo.lock:168

ASH leftover build, not leftover claim
  Cargo.lock:168    version = "0.3.0"
regenerate  cargo (Cargo.lock — lockfile)
```

Renamed ash dest (`generated/vendor_bundle.js` → `generated/out.js`) is still regenerate.

**3. JSON-only `plugin version 0.3.0` still resolves (full token, not `0.3`).**

```bash
./tinder --no-color -C kizu plugin/plugin.json:4
```

```
tinder: leftover  plugin/plugin.json:4

CLAIM "version": "0.3.0",
  plugin/plugin.json:4

FALSIFIED 53cbd1a055f5 chore: bump version to 0.3.1
FACT version: 0.3.0 → 0.3.1   Cargo.toml:3   score 103
```

October in `2024-10-01` is not integer 10. A dest leftover of timeout 10 that later moved still names the timeout bump, not the dest rename.
