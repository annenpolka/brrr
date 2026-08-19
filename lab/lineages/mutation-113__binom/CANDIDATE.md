# mutation-113 — binom

## Primitive

Leftover fact identity is `(crate/package, noun, dest)`. Given a leftover dest locus (`FILE:LINE`), emit the commit that falsified **that package's** claim. A homonym version (same noun, different crate) is not the falsifier. Ash answers **regenerate**.

smolder inverts leftover without workspace identity: two packages named `version` are one noun. tinder peels dest-file identity, not package identity. lien's natal is also one `VERSION` noun. Not leftover-name search.

## Why this might not exist

`git blame` on kizu `plugin.json:4` names `bff820fb` (when the leftover was written). smolder names `53cbd1a` Cargo.toml `0.3.0 → 0.3.1` (when a *different* package moved `version`). `git log -S 0.3.0` cannot tell plugin from crate. The dest line still claims plugin `0.3.0`, which is still true of the plugin.

The missing verb is: **this leftover claim, of this package, which commit made it false?** Homonym version must not win.

## How to run

From this worktree root (Python 3.9+, `git` on `PATH`, no other deps):

```bash
chmod +x ./binom ./demo.sh
./binom self-test
./demo.sh                 # exits 0; fixtures + gold kizu/sitbone if present
./binom --help
./binom -C <repo> path/to/file:LINE
printf 'pkg_b/README.md:1\n' | ./binom -C <repo>
```

Exit `0` found (falsifier or regenerate), `1` none, `2` usage/error.

## Empirical transcript

### Before the improvement (v0.1)

Workspace fixture: `pkg_a` 0.3.0→0.7.0, `pkg_b` still 0.3.0. smolder accuses `pkg_a/Cargo.toml` of `pkg_b`'s dest. binom does not:

```
$ ./binom --no-color --explain --no-hunk -C workspace pkg_b/README.md:1
binom: none  pkg_b/README.md:1  package cargo:pkg_b
  pkg_b version 0.3.0
  no falsifying fact mutation of this package.
# rc=1

$ ./binom --no-color --explain --no-hunk -C workspace pkg_b/Cargo.toml:3
binom: none  pkg_b/Cargo.toml:3  package cargo:pkg_b
  version = "0.3.0"
# rc=1

$ ./binom --no-color --explain --no-hunk -C workspace pkg_a/README.md:1
binom: leftover  pkg_a/README.md:1
CLAIM pkg_a version 0.3.0
FALSIFIED <sha> bump pkg_a only to 0.7.0
FACT version: 0.3.0 → 0.7.0   pkg_a/Cargo.toml:3   score 84  package cargo:pkg_a
# rc=0
```

Root README `pkg_b version 0.3.0 still ships with pkg_a.` names pkg_a on the line but the version claim is pkg_b's. Dest-line package bind is adjacency to `version` / the token, not any mention. none.

Gold kizu / sitbone:

```
$ ./binom --no-color --explain --no-hunk -C kizu plugin/plugin.json:4
binom: none  plugin/plugin.json:4  package plugin:kizu
  "version": "0.3.0",
  no falsifying fact mutation of this package.
# rc=1   not 53cbd1a, not Cargo.toml, not git blame bff820fb
```

`Cargo.lock:168` → `regenerate cargo`. Live `Cargo.toml:3` `0.7.0` is none of cargo:kizu.

```
$ ./binom --no-color --no-hunk -C sitbone CLAUDE.md:329
binom: leftover  CLAUDE.md:329
CLAIM @Test("… threshold 0.4）")
FALSIFIED e9b0f75deabd Implement dual-threshold hysteresis in PresenceArbiter
FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30   score 84
```

Same-package toy leftover still names the plugin.json bump (`package plugin:toy`) and the timeout on that line. Dest quote leftover-name with timeout still 10 is none (string kind opt-in). October ISO is not timeout 10.

`./demo.sh` → passed=61 failed=0.

v0.1 hole: none is silent. The homonym that was *not* the falsifier (`cargo:kizu` `0.3.0 → 0.3.1` at `53cbd1a`, `cargo:pkg_a` on pkg_b dest) is discarded. The invert answers "not this package" without naming the homonym.

### After the improvement (v0.2)

Forced by that silent-none transcript, not a feature list: **name the homonym that was not the falsifier.** none still exits 1. FALSIFIED is still reserved for *this* package.

```
$ ./binom --no-color --explain --no-hunk -C kizu plugin/plugin.json:4
binom: none  plugin/plugin.json:4  package plugin:kizu
  "version": "0.3.0",
  no falsifying fact mutation of this package.
  homonym cargo:kizu version 0.3.0 → 0.3.1   Cargo.toml:3   53cbd1a055f5 is not this package
# rc=1
```

```
$ ./binom --no-color --explain --no-hunk -C workspace pkg_b/README.md:1
binom: none  pkg_b/README.md:1  package cargo:pkg_b
  pkg_b version 0.3.0
  no falsifying fact mutation of this package.
  homonym cargo:pkg_a version 0.3.0 → 0.7.0   pkg_a/Cargo.toml:3   <sha> is not this package
# rc=1
```

sitbone `CLAUDE.md:329` still `e9b0f75` `0.4 → 0.45`. Cargo.lock still regenerate. Same-package leftover still FALSIFIED.

`./demo.sh` → passed=66 failed=0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| `fixtures/toy` | same-package plugin.json + timeout leftover | FALSIFIED plugin.json `package plugin:toy`; timeout 10→30 |
| workspace `pkg_a`/`pkg_b` | bump pkg_a only | pkg_b dest **none**; pkg_a README leftover of pkg_a |
| dest-hungry quote | timeout still 10, test string tweak | **none**, not `STR` leftover-name |
| ash lockfile | Cargo.lock dest | **regenerate cargo** |
| destroyer dates | CHANGELOG ISO vs `timeout default is 10` | October none; real timeout found |
| kizu `plugin/plugin.json:4` | current worktree | **none package plugin:kizu**; homonym `53cbd1a` Cargo.toml `is not this package` |
| kizu `Cargo.lock:168` | current worktree | **regenerate cargo** |
| sitbone `CLAUDE.md:329` / `:332` | current worktree | **e9b0f75 0.4→0.45 PresenceArbiter** |

## Surprises

- kizu plugin.json and Cargo.toml share the display name `kizu`. Package identity cannot be the name field. It is `(kind, manifest)`: `plugin:plugin/plugin.json` vs `cargo:Cargo.toml`.
- A dest line that *mentions* pkg_a while *claiming* pkg_b's version (`pkg_b version 0.3.0 still ships with pkg_a`) leftover-matches pkg_a if bind is "name appears". Adjacency to the noun `version` / the token is the dest component of the triple.
- Guessed manifest names (`plugin.json` at repo root → `plugin:plugin`) overwrite a parsed `"name": "toy"` if last-wins. First-wins keeps the parse.

## Failures

- Japanese as the binding still does not parse (`タイムアウト = 10`). Leftover Japanese of an English fact still matches via alias.
- Dest identity is not R records (tinder's peel). Dead dest names are `missing`.
- Size-cap dest is still silent `missing`. `vendor/` origin is still a believer.
- v0.1 none was silent; v0.2 prints the homonym. Japanese-as-binding / dest-rename / size-cap still unfixed.

## Suggested mutations

- Lockfile-only bump is still a fact for believer dest of *that* package, without blaming a later comment.
- Dates are not old integers even when the dest line says timeout.

## Kill / keep

**Keep.** The invert is still leftover-in / falsifier-out. Workspace identity makes homonym version fail closed. Gold sitbone `e9b0f75` still comes out. Gold kizu plugin.json is no longer Cargo.toml — that was the hole, not the product.
