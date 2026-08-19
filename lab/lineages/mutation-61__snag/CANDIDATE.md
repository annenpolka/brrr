# mutation-61 — snag

## Primitive

A unified diff is a superposition of syntactic classes. **snag** is the one-class tripwire: `--forbid CLASS` exits 1 if that ply moved, even when the rest of the patch is comments or docs.

weft projected onto one *allowed* class and failed if anything else leaked. snag inverts the question. Path does not free a hit. stdin is a unified diff. TSV only on `--emit`.

## Why this might not exist

Reviewers already say “the timeout moved” after a comment-only looking PR. weft `--only docs` answers a different question (*did any code ply leak?*) and frees documentation paths. Nobody asks the CI: *did a number ply move at all?*

The cheat is silent in two directions. A “docs PR” that bumped `30` to `60` on the same line as a comment. A genuine markdown commit that weft `--only docs` will pass while a timeout number still moved.

## How to run

```bash
./demo.sh
./snag --selftest
./snag --help
git diff | ./snag --forbid number
git diff | ./snag --forbid number --emit
git diff origin/main...HEAD | ./snag --forbid number
```

Python 3.9+, stdlib, no `git` required (stdin filter). Exit 0 = CLEAR, 1 = TRIP, 2 = usage.

`--forbid number` is the money shot. Comma lists work (`--forbid number,string`). `comments` / `code` are aliases for token classes, not path globs.

## Empirical transcript

### v0.1 — tripwire, not allow-list

`--selftest` 22/22. `./demo.sh` PASS=32 FAIL=0.

Fixture mixed line (weft fixtures, same stdin):

```
$ git diff | snag --forbid number
snag TRIP  forbid=number  stdin  files=1  hits=1  number=1
  src.rs:2  number  chg  30 → 60
# rc=1
$ git diff | snag --forbid number --emit
path	line	class	op	old	new
src.rs	2	number	chg	30	60
# rc=1; default (no --emit) is not TSV
```

Comment-only rewrite of `// secs` → `// timeout` is `snag CLEAR`. README `30 → 60` trips (`--forbid number` is not `*.md`). CJK prose `契約は蒸留 → 契約は資産` clears (class `text`).

Contrast with ancestor weft on the same stdin:

| fixture | weft `--only docs` | snag `--forbid number` |
| --- | --- | --- |
| mixed line `30→60` + comment | FAIL number | TRIP 30→60 |
| comment-only `secs→timeout` | OK | CLEAR |
| CJK README | OK | CLEAR |
| README `30→60` | OK (docs path) | **TRIP** |
| comment-interior `// timeout 30→60` | OK (comment ply) | **CLEAR (miss)** |
| docs PR + `src.rs` timeout | FAIL number | TRIP 30→60 |

Real repos (2026-08-20):

| commit | weft `--only docs` | snag `--forbid number` |
| --- | --- | --- |
| sitbone `e9b0f75` hysteresis | FAIL 414 (ident/kw/number flood) | **TRIP hits=28, numbers only.** First row `0.4 → 0.45` |
| sitbone `8b1d0f2` timeout | FAIL 119 | TRIP hits=10 (`10`, `5.0`, `30.0`, `400`) |
| sitbone `77df1da` README+Makefile | FAIL 21, Makefile only | TRIP hits=2: Makefile `2` (`2>/dev/null`). README `2048` is inside a fenced ` ```bash ` string |
| sitbone `98a8009` ADR | **OK leaked=0** | **TRIP hits=90** (`0.4`, `0.45`, `2026`, `0019`) |
| voidtrace `ce44c93` docs CI | **OK leaked=0** | **TRIP hits=10** (`2026`, `30705844166`, hash `557`) |
| kizu `9349dc5` release | FAIL string `0.6.0→0.7.0` | **CLEAR** (version is a string ply; lock skipped) |

The required contrast is honest on two real commits: **weft `--only docs` passes and snag `--forbid number` trips** on sitbone ADR and voidtrace docs-ci. The reverse is also honest: kizu’s version bump is a *string*, so weft fails and v0.1 snag clears.

### v0.2 — peel numbers out of comment/string interiors

Forced by the v0.1 transcript, not by taste:

1. `// timeout 30` → `// timeout 60` is the cheat weft named. Surface class is `comment`. v0.1 cleared it. weft `--only docs` still passes.
2. kizu `version = "0.6.0"` → `"0.7.0"` is a string ply. `--forbid number` cleared a real version bump.
3. sitbone `77df1da` README `default_bits = 2048` lives inside a markdown ` ```bash ` fence. The shared lexer treats the fence as one backtick-string. v0.1 never saw 2048.

v0.2 scans comment / string / key / import bodies for number tokens and projects those as class `number`. `--selftest` 26/26. `./demo.sh` PASS=35 FAIL=0.

```
$ git diff   # let timeout = 30; // timeout 30  →  // timeout 60
$ weft --only docs
weft OK  only=docs  stdin  files=1  leaked=0
$ snag --forbid number
snag TRIP  forbid=number  stdin  files=1  hits=1  number=1
  src.rs:2  number  chg  30 → 60
```

| object | v0.1 | v0.2 |
| --- | --- | --- |
| comment-interior `30→60` | CLEAR | **TRIP 30→60** |
| kizu `9349dc5` `"0.6.0"→"0.7.0"` | CLEAR | **TRIP `0.6 → 0.7`** (lock still skipped) |
| sitbone README `2048` in fence | CLEAR | **TRIP 2048, 3650** |
| sitbone `e9b0f75` | TRIP 28 | TRIP 78 — new comments mentioning `ADR-0019` / `0.45` peel as inserts; `0.4→0.45` still first |
| voidtrace `ce44c93` | TRIP 10 | TRIP 15 — hash `6e3368b` peels as scientific `6e3368` |

The money contrast is now a fixture, not only a docs-path accident: **`--only docs` passes and `--forbid number` fails** on the comment-interior timeout.

## Dogfood targets

- weft fixtures in `./demo.sh` (mixed line, comment-only, README+timeout, comment-interior).
- sitbone `e9b0f75` (threshold number + comments), `8b1d0f2` (timeout), `77df1da`, `98a8009`.
- voidtrace `ce44c93`.
- kizu `9349dc5`.

## Surprises

- Same-line superposition works as a tripwire: comment ply is ignored, number ply trips, `--emit` prints only the forbidden class. weft’s 414-leak hysteresis commit collapses to numbers (28 surface, 78 after peel).
- Path-free is the point. ADR `0.4` and voidtrace run ids are number plies. weft freed them because they live on documentation paths. snag does not become `*.md`.
- Markdown fences are backtick *strings*. That one lexer fact hid sitbone’s `2048` and kizu’s `0.6.0` the same way a comment hid `timeout 30`. Peel is one patch for three hides.
- `2>/dev/null` in a Makefile is a number ply. Honest, a bit sad.
- `6e3368b` peels as scientific notation `6e3368`. The hash was already a weft split; peel made it louder.

## Failures

- Peel makes new comments noisy: `/// ADR-0019` is a number insert. hysteresis 28→78. The timeout *chg* is still in the list.
- Hyphenated hashes (`557c76f`) still split; voidtrace trips on `557` and now on `6e3368`.
- Dates in genuine docs commits (`2026-08-01`) are number inserts. `--forbid number` on a “record the CI run” PR will trip. That is the object, not a path bug.
- Semver `"0.6.0"` peels as `0.6` + `0`, not one token. Enough to trip. Ugly under `--emit`.
- Punct/space ignored unless forbidden.

## Suggested mutations

- `--chg`: trip only on value changes (`30→60`), not on every inserted date / ADR-0019 in a new comment. The peel made this more urgent.
- Hex/hash tokens so `557c76f` / `6e3368b` are one ident, not a number.
- Semver as one number token.
- GitHub Actions annotation from `--emit`.

## Kill / keep

**Keep.** The default is a verdict a CI job can fail on: `git diff | snag --forbid number`. The mixed-line timeout is the review cheat weft named and never made the product. v0.2 is the one improvement the transcript forced: the same cheat inside a comment, a version string, or a markdown fence is still a number ply. `--only docs` can pass that line. `--forbid number` cannot.
