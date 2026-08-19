# mutation-32 — ember

## Primitive

Print leftover claims a diff just made false. Facts are typed: a version is the full token, a calendar month is not an integer, a quoted JSON key is a binding.

A *fact* is a bound name/value, rename, or polarity flip extracted from a unified diff. An *afterimage* is a remaining comment, doc, test, string, or config line in the destination tree that still asserts the old fact. Exit `0` if the destination has no afterimages, `1` if any remain (linter-composable), `2` on error.

Parents: **zanei** (candidate-07, 残影) is blind to JSON-only hunks. **nagori** (reimpl-03, 名残) extracts `"version": "0.3.0"` then truncates the dest bind to `0.3` and throws the prose leftover away. DESTROYER_ZANEI: mutate both; next mutation is typed facts with token boundaries.

## Why this might not exist

`rg` can find a token. `git grep` can find it at a revision. Neither knows that *this diff* changed `timeout: 10 → 30` or `"version": "0.3.0" → "0.7.0"`, so they cannot ask: **what else in the tree still believes the old fact?**

zanei answers a narrower question (unquoted bindings). nagori answers the JSON question and then discards the common leftover sentence `plugin version 0.3.0` because `NUMBER_RE = \d+(?:\.\d+)?` binds `version = 0.3`. The missing verb is still "belie", but the fact has to be typed or the leftover is the wrong object.

## How to run

From this worktree root (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./ember ./demo.sh
./ember self-test
./demo.sh                 # exits 0; includes destroyer JSON + date-in-version
./ember --help
./ember -C <repo>         # HEAD → worktree
./ember -C <repo> A B     # tree A → tree B, search B
git diff A B -- path | ./ember --diff - -C <repo>
```

## Empirical transcript

### Before the improvement (v0.1)

Typed extraction + typed needles, still a believer in leftover `True` that only neighbors the name.

Toy fixture, implementation changed, claims left behind: `./demo.sh` → `passed=40 failed=0` (43 after the v0.2 polarity checks).

Destroyer JSON-only hunk (`"version": "0.3.0"` → `"0.7.0"`). zanei: `0 fact(s)`. nagori: extracts the fact, then `homonym_skip` because dest prose binds `version = 0.3`. ember:

```
$ cat plugin.diff | ./ember --facts-only --diff - -C $KIZU
ember: 1 fact(s)  diff → worktree
  value    version: '0.3.0' → '0.7.0'  (plugin.json:3)

$ cat plugin.diff | ./ember --explain --diff - -C $KIZU
ember: 1 afterimage  diff → worktree

FACT version: 0.3.0 → 0.7.0   plugin.json:3
   84 docs    README.md:1   plugin version 0.3.0, hook timeout 10 seconds.
```

The leftover is the full token. It is not gated. It is not `0.3`.

Destroyer date-in-version. Isolated `HOOK_TIMEOUT = 10 → 30` against dest `## timeout` / `shipped 2024-10-01`: **0 afterimages** (October is not integer 10). A real `timeout default is 10` on the same tree still fires; the date line does not. Isolated `MAX_RETRIES = 3 → 8` finds `retries=3` and does not find a date-only `2024-03-01`.

Gold cases unchanged from both parents:

```
$ git -C kizu diff v0.3.0 v0.7.0 -- Cargo.toml | ./ember --diff - -C kizu --min-score 70
ember: 3 afterimages

FACT version: 0.3.0 → 0.7.0   Cargo.toml:3
  103 config  plugin/plugin.json:4    "version": "0.3.0",
   84 docs    plans/v0.3.md:103       - [ ] version bump to 0.3.0
   84 docs    plans/v0.3.md:451       "version": "0.3.0"

$ ./ember --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 55
ember: 2 afterimages

FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30
   84 docs    CLAUDE.md:329   @Test("… threshold 0.4）")
   84 docs    CLAUDE.md:332   @Test("… threshold 0.4）")
```

JSON-only path into the same kizu dest (synthetic plugin.json hunk) recovers plugin.json at 115 plus the two plan lines at 84 — the gold finding from the JSON side of the skew.

Tenaoshi `3798ea7 --min-score 60`: 5 `intent` facts, 26 afterimages (same as both parents).

Voidtrace `6e3368b --min-score 60`: 7 facts (parents' 5 coverage counts plus two JSON `sourceFingerprint` hashes from quoted keys), **0 afterimages**.

Binary stdin / `--diff FILE` with high bytes: exit **2** (fail closed). Empty `--kinds`: exit **2**.

`café_timeout = 10 → 30` extracts `café_timeout`, not a minted `_timeout`. `DEBUG = True → False` is a named polarity. `timeout` ⊄ `settimeout`. `present` ⊄ `presentation`.

### After the improvement (v0.2)

v0.1 still treated a boolean as distinctive enough to ride a nearby name. DESTROYER_ZANEI § nagori.2: `ENABLE_CACHE: True → False` leftover-matched `DEBUG is True` because window-3 reached `the cache is enabled`.

Measured on a dest that contains both the real leftover and the ghost:

```
# v0.1
FLIP ENABLE_CACHE: True → False
   84 docs    README.md:5   assert ENABLE_CACHE is True
   76 docs    README.md:3   DEBUG is True
         why: nearby-name, name-stem, old-value, claim:docs
```

v0.2: polarity leftovers require a **same-line** name or stem. Nearby `cache` plus a stray `True` is not this flip.

```
# v0.2
FLIP ENABLE_CACHE: True → False
   84 docs    README.md:5   assert ENABLE_CACHE is True

$ ./ember self-test
  ok  polarity leftover needs same-line name
  ok  ENABLE_CACHE is True still scores
```

Gold kizu / sitbone / tenaoshi / destroyer JSON / date cases unchanged. Integer facts may still use nearby-name (`## timeout` + a real `10`). `./demo.sh` → `passed=43 failed=0`.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| `fixtures/toy` | worktree + `HEAD~1 HEAD` | intended leftovers, including `plugin version 0.3.0` |
| `fixtures/ugly` | spaces / `日本語コメント.md` / `🌀 leftover.md` / nested git | names work; nested note visible |
| destroyer JSON hunk | `--diff` quoted `"version"` vs dest prose | **1 fact, 1 leftover**, full `0.3.0` |
| destroyer dates | isolated `HOOK_TIMEOUT` / `MAX_RETRIES` | October/March not leftovers; real sentences are |
| kizu `v0.3.0..v0.7.0` Cargo.toml | `--diff - --min-score 70` | **exact** plugin.json 103 + two plan 84 |
| kizu JSON-only synthetic | `--diff` plugin.json | plugin.json + two plan lines |
| sitbone `e9b0f75` | `--min-score 55` | **exact** 2 CLAUDE.md `threshold 0.4` |
| tenaoshi `3798ea7` | `--min-score 60` | 5 facts, 26 afterimages |
| voidtrace `6e3368b` | `--min-score 60` | 7 facts, 0 afterimages |

## Surprises

- The kizu plugin manifest is reachable from **either** side of the skew: Cargo.toml (zanei's gold path) or a JSON-only plugin hunk (nagori's grammar without nagori's truncation).
- `3` already failed to match `2024-03-01` (leading zero). The live hole was only `10` inside `2024-10-01`. Masking calendar tokens is enough; adding `-` to the number class is not a date theory.
- Quoted-key grammar also names `sourceFingerprint` hashes on voidtrace. They did not explode the afterimage list at 60.

## Failures

- **v0.1 polarity nearby-True:** a boolean is not a distinctive value. Fixed in v0.2 by requiring a same-line name/stem.
- **Still failing:** no language parser. Historical trees do not recurse nested repos. Japanese bindings still do not parse (`タイムアウト = 10` is not a fact; leftover Japanese of an *English* fact still matches via the alias table). Fullwidth `１０` is not `10`. `generated/` dest files still score like forgotten claims (a leftover *build*, not a leftover *claim*). Size-cap omit is silent. Two packages named `version` are one noun.

## Suggested mutations

- Skip dest `generated/` (and warn on size-cap omit) so a regenerated oracle is not a believer.
- Learn aliases from the repo instead of a hard-coded table.
- `ember blame <path>:<line>`: invert the verb — given a claim, show the diff that falsified it.
- Workspace identity so `pkg_a` version 0.3.0→0.7.0 does not accuse `pkg_b`.

## Kill / keep

**Keep.** The object is still leftover *claims*. The mutation is the type of the fact (version token, calendar-not-integer, JSON key, polarity-needs-a-name), not a smarter walk. Gold kizu and sitbone still come out. The destroyer JSON sentence survives.
