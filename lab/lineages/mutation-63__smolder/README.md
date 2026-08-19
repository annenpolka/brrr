# smolder (mutation-63)

Leftover **claim** in, falsifying **diff (commit)** out.

zanei / ember / cinder take a diff and print leftover afterimages. **smolder** inverts the verb: given a dest locus (`FILE:LINE` or stdin locators), name the change that made that claim false.

A *fact* is a typed bound name/value, rename, or polarity flip (ember). Regenerated dest (`generated/`, `oracle/`, lockfile, `*.generated.*`, `@generated` banner) is **ash**: leftover *build*. Ash answers **regenerate** (and the generator if known), not "edit this line". A believer leftover names the falsifying commit and origin hunk.

Not leftover names (haunt / wraith). `FILE:LINE` is legal **input** here.

## Install / run

Python 3.9+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./smolder ./demo.sh
./smolder self-test
./demo.sh                 # fixtures + gold kizu/sitbone if present; exits 0
./smolder --help
```

Exit codes: `0` found (falsifier or regenerate), `1` none, `2` usage/error.

```bash
./smolder -C <repo> path/to/file:LINE
printf 'README.md:7\n' | ./smolder -C <repo>
git diff A B | ./smolder --diff - -C <repo> leftover.md:3
```

## Examples

**1. Docs leftover names the commit that moved the fact.**

```bash
./smolder --no-color -C sitbone CLAUDE.md:329
```

```
smolder: leftover  CLAUDE.md:329

CLAIM @Test("… threshold 0.4）")
  CLAUDE.md:329

FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

The dest line still teaches `threshold 0.4`. PresenceArbiter moved it to `0.45`.

**2. A generated lockfile leftover is ash — regenerate, do not blame a comment.**

```bash
./smolder --no-color -C kizu Cargo.lock:168
```

```
smolder: ash  Cargo.lock:168

ASH leftover build, not leftover claim
  Cargo.lock:168    version = "0.3.0"
regenerate  cargo (Cargo.lock — lockfile)
```

**3. JSON-only `plugin version 0.3.0` still resolves (full token, not `0.3`).**

```bash
./smolder --no-color -C kizu plugin/plugin.json:4
```

```
smolder: leftover  plugin/plugin.json:4

CLAIM "version": "0.3.0",
  plugin/plugin.json:4

FALSIFIED 53cbd1a055f5 chore: bump version to 0.3.1
FACT version: 0.3.0 → 0.3.1   Cargo.toml:3   score 103
```

October in `2024-10-01` is not integer 10: pointing at a date-only changelog line exits `1`, while `timeout default is 10` on the same tree names the timeout bump.

A dest line that leftover-claims several facts from the same commit prints all of them (not only the highest score): `plugin version 0.3.0, hook timeout 10 seconds` names both the JSON version bump and `HOOK_TIMEOUT: 10 → 30`.
