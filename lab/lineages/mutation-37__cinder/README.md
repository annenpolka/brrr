# cinder (mutation-37)

Leftover **claims** a diff made false. A regenerated dest file is **ash, not a believer**.

A *fact* is a typed bound name/value, rename, or polarity flip in a unified diff (ember's extractor: a version is the full token, a calendar month is not an integer, a quoted JSON key is a binding). An afterimage in docs, tests, or source is a leftover *claim*. An afterimage in `generated/`, `oracle/`, lockfiles, `*.generated.*`, or a `@generated` banner is a **cinder** — leftover *build*, not a linter failure.

Parents: **zanei** skipped `vendor/` and treated `generated/` as a believer. **ember** typed the fact but still scored dest `generated/` like a forgotten claim. DESTROYER_ZANEI: a regenerated oracle is leftover *build*.

## Install / run

Requires Python 3.10+ and `git` on `PATH`. No other dependencies.

```bash
chmod +x ./cinder ./demo.sh
./cinder --help
./cinder self-test
./demo.sh          # fixture tests + gold kizu/sitbone if present; exits 0
```

Exit codes: `0` no leftover *claims* (cinders do not count), `1` leftover claims, `2` usage/error.

Default comparison is `HEAD` → working tree. Output is human text; `--tsv` and `--json` are pipeable. `--include-generated` prints ash without promoting it to exit 1.

```bash
git diff A B | ./cinder --diff - -C repo
```

## Examples

**1. Docs leftover is a claim; generated/oracle/lockfile leftovers are ash.**

```bash
git diff HEAD | ./cinder --diff - -C .
```

```
cinder: 3 leftovers  HEAD → worktree

FACT TIMEOUT: 10 → 30   src/config.py:1
   84 docs    README.md:1   timeout default is 10

FACT version: 0.3.0 → 0.7.0   plugin.json:3
   84 docs    README.md:2   plugin version 0.3.0

  11 cinders (regenerated dest; not leftover claims). --include-generated to see ash.
```

`generated/vendor_bundle.js`, `oracle/timeout.json`, `Cargo.lock`, and a `@generated` oracle are not leftover claims. They do not flip the exit code.

**2. See the ash without failing on it.**

```bash
git diff HEAD | ./cinder --diff - -C . --include-generated
```

```
11 cinders (ash, not leftover claims)

CINDER version: 0.3.0 → 0.7.0   plugin.json:3
  103 cinder  Cargo.lock:6           version = "0.3.0"
  103 cinder  package-lock.json:7    "version": "0.3.0"

CINDER TIMEOUT: 10 → 30   src/config.py:1
   88 cinder  oracle/timeout.json:1  {"timeout": 10, "retries": 3}
   72 cinder  generated/vendor_bundle.js:2  const TIMEOUT = 10;
```

Exit is still `1` only because README still believes the old facts. An ash-only dest exits `0`.

**3. Historical range / someone else's patch (kizu gold).**

```bash
git diff v0.3.0 v0.7.0 -- Cargo.toml | ./cinder --diff - -C kizu --min-score 70
```

```
cinder: 3 leftovers  diff → worktree

FACT version: 0.3.0 → 0.7.0   Cargo.toml:3
  103 config  plugin/plugin.json:4    "version": "0.3.0",
   84 docs    plans/v0.3.md:103       - [ ] version bump to 0.3.0
   84 docs    plans/v0.3.md:451       "version": "0.3.0"
```

`Cargo.lock` still has `version = "0.3.0"`. That is ash (`--include-generated`), not a leftover claim. `plugin.json` is a believer.
