# reimpl-03 — nagori (名残)

## Primitive

Print leftover claims a diff just made false.

A *fact* is a bound name/value, rename, or polarity flip extracted from a unified diff. An *afterimage* is a remaining comment, doc, test, string, or config line in the destination tree that still asserts the old fact. Exit `0` if the destination has no afterimages, `1` if any remain (linter-composable), `2` on error.

This is a from-behavior reimplementation of `zanei` (candidate-07). The original Python file was never opened. CLI shape, fixtures, self-test labels, and dogfood queries were recovered by running the original binary and reading its README / CANDIDATE / demo.

## Why this might not exist

`rg` can find a token. `git grep` can find it at a revision. Neither knows that *this diff* changed `timeout: 10 → 30` or `MAX_RETRIES → MAX_ATTEMPTS`, so they cannot ask the only question that matters after an edit: **what else in the tree still believes the old fact?**

Rebuilding from the outside tests whether the primitive is real or an accident of one implementation.

## How to run

From this worktree root (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./nagori ./demo.sh
./nagori self-test
./demo.sh                 # exits 0
./nagori --help
./nagori -C <repo>         # HEAD → worktree
./nagori -C <repo> A B     # tree A → tree B, search B
git diff A B -- path | ./nagori --diff - -C <repo>
```

## Empirical transcript

### Before the improvement (v0.1)

Toy fixture, implementation changed, claims left behind: `./demo.sh` → `passed=24 failed=0`.

Side-by-side with original `zanei` on the two required gold cases (never reading its source):

```
$ ./nagori --facts-only --no-color -C sitbone e9b0f75^ e9b0f75
nagori: 2 fact(s)  e9b0f75^ → e9b0f75
  rename   threshold: 'threshold' → 'presentThreshold'  (Sources/SitboneCore/PresenceArbiter.swift:30)
  value    threshold: '0.4' → '0.45'  (Sources/SitboneCore/PresenceArbiter.swift:30)

$ ./nagori --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 55
nagori: 2 afterimages  e9b0f75^ → e9b0f75

FACT threshold: 0.4 → 0.45   Sources/SitboneCore/PresenceArbiter.swift:30
   84 docs    CLAUDE.md:329   @Test("カメラのみpresent → 総合present（weight 0.50 > threshold 0.4）")
   84 docs    CLAUDE.md:332   @Test("idleのみpresent → 総合absent（weight 0.05 < threshold 0.4）")

$ ./nagori --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 50
nagori: 3 afterimages
  … plus ADR-0019:76 (score 52, file-has-new)
```

Matches `zanei` exactly: same two facts, same two CLAUDE.md leftovers at default 55, same ADR line at 52. SiteObserver's homonym `threshold = 0.7` is absent.

```
$ git -C kizu diff v0.3.0 v0.7.0 -- Cargo.toml | ./nagori --diff - -C kizu --min-score 70
nagori: 3 afterimages  diff → worktree

FACT version: 0.3.0 → 0.7.0   Cargo.toml:3
  103 config  plugin/plugin.json:4    "version": "0.3.0",
   84 docs    plans/v0.3.md:103       - [ ] version bump to 0.3.0
   84 docs    plans/v0.3.md:451       "version": "0.3.0"
```

Scores, claims, paths, and why-tags (`same-line-name, old-value, claim:config, version-config`) match `zanei` byte-for-byte on the human output.

Tenaoshi palette rename (`3798ea7`): 5 `intent` facts (`整えて` → `Tidy`, …) and **26** afterimages — same count as `zanei`.

**v0.1 gap:** a JSON-only version hunk is invisible as a named fact (quoted `"version":` is not an unquoted binding). `zanei` is also silent. `plugin.json` leftovers are only found when some *other* file (Cargo.toml) supplies the fact.

```
$ git diff -- plugin.json | ./nagori --diff - --facts-only
nagori: 1 fact(s)   # string '0.3.0' → '0.7.0' only; no value named version
```

Voidtrace `6e3368b` still invents kebab fragments (`ritical-tier` from `Critical-tier`) and explodes to hundreds of afterimages. `zanei` v0.2 keeps 5 coverage-count facts and 0 afterimages at `--min-score 60`.

### After the improvement (v0.2)

Two v0.1 holes, both measured against live diffs:

1. **Quoted JSON keys.** A plugin-manifest version hunk is now a named fact:

```
$ git diff -- plugin.json | ./nagori --diff - --facts-only
nagori: 1 fact(s)  diff → worktree
  value    version: '0.3.0' → '0.7.0'  (plugin.json:2)
```

`zanei` still reports `0 fact(s)` on that hunk. Searching kizu for leftovers of this fact still ranks `plugin/plugin.json` at 103 — same gold finding, now reachable from *either* side of the skew.

2. **Word-bounded kebab tokens.** `Critical-tier` no longer yields a phantom `ritical-tier` rename. Voidtrace `6e3368b` dropped the two fragment remames (`27 → 25` facts). Remaining noise is real code remames (`evaluateMember` → `evaluateScenario`) that `zanei` v0.2 refuses by a stricter "code-shaped + not-inflection + old-ident-gone" filter.

Gold cases **unchanged**:

- sitbone `e9b0f75` `--min-score 55`: 2 afterimages, both CLAUDE.md `threshold 0.4`
- kizu Cargo.toml `v0.3.0..v0.7.0` `--min-score 70`: plugin.json 103 + two `plans/v0.3.md` 84
- tenaoshi `3798ea7 --min-score 60`: 5 facts, 26 afterimages
- `./demo.sh`: `passed=27 failed=0` (24 original + 3 JSON-key checks)

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| `fixtures/toy` | worktree + `HEAD~1 HEAD` | 12 afterimages, intended leftovers |
| `fixtures/ugly` | spaces / `日本語コメント.md` / `🌀 leftover.md` / nested git | names work; nested note visible |
| sitbone `e9b0f75` | vs original `zanei` | **exact** 2 facts / 2 afterimages @55 |
| kizu `v0.3.0..v0.7.0` Cargo.toml | `--diff -` | **exact** plugin.json 0.3.0 + two plan lines |
| tenaoshi `3798ea7` | intents → English names | 5 facts, 26 afterimages |
| voidtrace `6e3368b` | v0.1 | noisy remames (known gap) |
| skills `6b19433` | markdown tweak | no leftover afterimages |

## Surprises

- The kizu plugin manifest is a live inconsistency (crate `0.7.0`, plugin `"version": "0.3.0"`) recovered from a two-line Cargo.toml hunk — same "why doesn't this exist?" moment as `zanei`.
- Scoring tags reverse-engineered from `--explain` / `--json` (`same-line-name` +40, `old-value` +20, `claim:config` +28, `version-config` +15, `file-has-new` −32, …) reproduced the gold scores exactly.
- JSON files produce no *named* facts until quoted keys are parsed; leftover *search* in `.json` still works.

## Failures

- **v0.1 voidtrace remames:** kebab regex matched inside `Critical-tier`. Fixed in v0.2 by word-bounding kebab tokens. Larger identifier remames on that commit remain (stricter than v0.1, noisier than `zanei` v0.2).
- **v0.1 JSON facts:** `"version":` ignored as a binding. Fixed in v0.2.
- **Still failing:** no language parser. Historical trees do not recurse nested repos. Japanese aliases are a tiny table. Tenaoshi leftover `整えて` may be an intentional free-text path.

## Suggested mutations

- `nagori blame <path>:<line>`: invert the verb — given a claim, show the diff that falsified it.
- Learn aliases from the repo instead of a hard-coded table.
- Tree-sitter bindings so facts are symbols, not regex pairs.

## Kill / keep

**Keep.** Independent reimplementation recovered the same sitbone 0.4 leftovers and the same kizu version skew without reading the original source. The primitive is the interaction, not the file.
