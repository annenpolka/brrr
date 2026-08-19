# binom (mutation-113)

Leftover **claim** in, falsifying **diff (commit)** of *that package* out.

smolder inverts leftover: dest locus in, falsifying commit out. Hole: two packages named `version` are one noun. `plugin/plugin.json` leftover-matches a Cargo.toml bump; `pkg_b` leftover-matches `pkg_a`. That is a homonym, not a falsifier.

**binom** peels workspace identity. Leftover fact identity is `(crate/package, noun, dest)`. The falsifying commit must change *that* package's version. A homonym version is not the falsifier.

A *fact* is a typed bound name/value, rename, or polarity flip. Regenerated dest (`generated/`, `oracle/`, lockfile, `@generated` banner) is **ash**: leftover *build*. Ash answers **regenerate**. Default kinds are `value,rename,polarity` (string is leftover-name, opt-in).

Not leftover names (haunt / wraith). `FILE:LINE` is legal **input**.

## Install / run

Python 3.9+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./binom ./demo.sh
./binom self-test
./demo.sh                 # fixtures + gold kizu/sitbone if present; exits 0
./binom --help
```

Exit codes: `0` found (falsifier or regenerate), `1` none, `2` usage/error.

```bash
./binom -C <repo> path/to/file:LINE
printf 'pkg_b/README.md:1\n' | ./binom -C <repo>
git diff A B | ./binom --diff - -C <repo> leftover.md:3
```

## Examples

**1. Two crates named `version` are two packages.** `pkg_a` 0.3.0→0.7.0 does not falsify `pkg_b` 0.3.0.

```bash
./binom --no-color -C workspace pkg_b/README.md:1
```

```
binom: none  pkg_b/README.md:1  package cargo:pkg_b
  pkg_b version 0.3.0
  no falsifying fact mutation of this package.
  homonym cargo:pkg_a version 0.3.0 → 0.7.0   pkg_a/Cargo.toml:3   <sha> is not this package
```

The same bump still falsifies `pkg_a/README.md` (`FACT version: 0.3.0 → 0.7.0` `package cargo:pkg_a`).

**2. kizu plugin.json vs Cargo.toml.** The Claude plugin and the crate share the display name `kizu` and the noun `version`. They are not one package. smolder accuses `53cbd1a` Cargo.toml `0.3.0 → 0.3.1`. binom does not.

```bash
./binom --no-color -C kizu plugin/plugin.json:4
```

```
binom: none  plugin/plugin.json:4  package plugin:kizu
  "version": "0.3.0",
  no falsifying fact mutation of this package.
  homonym cargo:kizu version 0.3.0 → 0.3.1   Cargo.toml:3   53cbd1a055f5 is not this package
```

Named lockfile dest is still ash: `Cargo.lock:168` → `regenerate cargo`.

**3. Non-version leftover is unchanged.** sitbone `CLAUDE.md:329` still names `e9b0f75` `threshold 0.4 → 0.45`.

```bash
./binom --no-color -C sitbone CLAUDE.md:329
```

```
binom: leftover  CLAUDE.md:329

CLAIM @Test("… threshold 0.4）")
  CLAUDE.md:329

FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

October in `2024-10-01` is not integer 10. A dest quote leftover-name (`"toy hook-post-tool"`) with timeout still 10 is **none**, not `STR`.
