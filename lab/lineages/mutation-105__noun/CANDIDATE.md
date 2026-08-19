# mutation-105 — noun

## Primitive

`git diff | noun` is a CI gate on leftovers of that change's **(package, noun)** natal. Two packages named `version` are two nouns. A plugin.json version leftover is not cleared by Cargo.toml `0.3.0→0.3.1`. Same advertised name across sibling manifests (`crate:kizu` / `plugin:kizu`) is one product noun; `clap.version` is not.

Default input is a unified diff on stdin. Default output is `--check`: one dest-line lien, silent on success, exit 1 if dest still speaks that record as *current*. `--explain` is the human natal dump.

Not leftover-name search. Not a fourth cinch. Binding leftovers (`t1`, `threshold`) stay un-gated by package.

## Why this might not exist

lien (mutation-57) is a real natal-record gate: `t1↔driftDelay` both-rows and sitbone `CLAUDE.md:329` fail CI. DESTROYER_LIEN §6: `merge_natals` groups by `ident_parts("version")`, so `cli` + `core` collapse and kizu `plugin.json` `0.3.0` is a homonym of Cargo `0.6.0→0.7.0`. A release CI job `git diff origin/main...HEAD | lien` is green while the Claude plugin still advertises 0.3.0.

tinder inverts dest leftover → falsifying commit and treats `plugin.json:4` as leftover of `53cbd1a` Cargo.toml. That is dest-locus invert, not a CI gate on stdin, and it still has one `version` noun.

Discarded as concatenation: `lien | grep plugin.json`. That still cannot mint the core crate's natal. Discarded: failing every docs hit of the word `version` (`--all` already does that, 28 kin). Discarded: leftover-name haunt. Discarded: a fourth cinch.

The missing verb is: **this change's version, whose package, which dest manifest still speaks it.**

## How to run

From this worktree (Python 3.10+, `git` on `PATH`, no other deps):

```bash
chmod +x ./noun ./demo.sh
./noun self-test
./demo.sh
./noun --help
git diff | ./noun
git diff | ./noun --facts-only
git diff | ./noun --explain
git -C kizu diff 9349dc5^ 9349dc5 | ./noun -C kizu
git -C sitbone diff e9b0f75^ e9b0f75 | ./noun -C sitbone
```

Exit `0` none, `1` leftovers, `2` usage/error. `FILE:LINE` exits 2.

## Empirical transcript

### Before the improvement (v0.1)

Workspace fixture, bump only `cli` `0.3.0→0.7.0`, `core` stays `0.3.0`:

```
$ git diff HEAD^ HEAD | ./noun --facts-only
noun: 1 natal record(s)  diff → worktree
  value    crate:cli VERSION  0.3.0 → 0.7.0  (crates/cli/Cargo.toml:3)

$ git diff HEAD^ HEAD | ./noun
README.md:1: claim: crate:cli VERSION  0.3.0 → 0.7.0: cli 0.3.0 and core 0.3.0 ship together.
# rc=1
# crates/core/Cargo.toml is absent (lien failed it as leftover of cli)
```

Bump both, different versions:

```
$ git diff HEAD^ HEAD | ./noun --facts-only
noun: 2 natal record(s)
  value    crate:cli VERSION  0.3.0 → 0.7.0
  value    crate:core VERSION  1.2.0 → 1.3.0
```

lien minted 1 natal and dropped `1.2.0→1.3.0`.

kizu `9349dc5` (lien: silent rc=0, 28 kin under `--all`, plugin.json in neither):

```
$ git diff 9349dc5^ 9349dc5 | ./noun --facts-only -C kizu
noun: 1 natal record(s)  diff → worktree
  value    crate:kizu VERSION  0.6.0 → 0.7.0  (Cargo.lock:920)

$ git diff 9349dc5^ 9349dc5 | ./noun --no-color -C kizu
plugin/plugin.json:4: claim: crate:kizu VERSION  0.6.0 → 0.7.0: "version": "0.3.0",
# rc=1  one dest-line. clap 4.6.0 absent. no : kin:
```

kizu `53cbd1a` (`0.3.0→0.3.1`):

```
plugin/plugin.json:4: both: crate:kizu VERSION  0.3.0 → 0.3.1: "version": "0.3.0",
```

The crate bump does not clear the plugin leftover.

sitbone `e9b0f75` gold holds: 12 current liens, 4 `via=both`, `CLAUDE.md:329` / `:332`, no `v0.4`, no kin. `--explain` 16 leftovers, one natal `threshold↔presentThreshold`.

Wrong object, forced by that run:

1. **Natal origin is Cargo.lock:920.** The package bump was `Cargo.toml`. Lockfile is the first valued natal in diff order. The (package, noun) is right; the origin path is the lock, not the manifest.

`./demo.sh` → passed=50 failed=0. `./noun self-test` 0.

### After the improvement (v0.2)

Forced by that kizu `9349dc5` facts-only line, not a feature list:

1. **Emit must not collapse two origin paths before merge.** `natal.key()` is `(package, noun, old, new)`. Cargo.lock minted first; Cargo.toml was dropped as a duplicate. Merge never saw the manifest.
2. **Prefer a named manifest over a lockfile** as origin (`Cargo.toml` / `plugin.json` / `package.json` / `pyproject.toml` beat `Cargo.lock`).

```
$ git diff 9349dc5^ 9349dc5 | ./noun --facts-only -C kizu
noun: 1 natal record(s)  diff → worktree
  value    crate:kizu VERSION  0.6.0 → 0.7.0  (Cargo.toml:3)
```

Self-test puts the lockfile *first* in the diff (the real commit order) and still attributes origin to `Cargo.toml`. plugin.json still fails as the sibling leftover. sitbone gold unchanged (12 current, 4 both, CLAUDE.md:329/332). `./demo.sh` → passed=51 failed=0.

## Dogfood targets

| Target | What was run | Outcome |
| --- | --- | --- |
| workspace fixture (demo.sh) | bump only cli; bump both | core manifest quiet; two natals when both move |
| t1 binding | `t1=15` → `driftDelay=15` | `T1 is 15 seconds` via=both |
| kizu `9349dc5` | crate 0.6.0→0.7.0, dest plugin 0.3.0 | lien green; noun `plugin.json:4` rc=1, 1 dest-line |
| kizu `53cbd1a` | crate 0.3.0→0.3.1 | plugin.json still unpaid |
| sitbone `e9b0f75` | hysteresis | 12 current, 4 both, CLAUDE.md:329/332, no v0.4 |
| clap dep | dest `version = "4.6.0"` | not leftover of kizu.version |

## Surprises

- Same advertised *name* is the split key, not origin kind. `crate:kizu` and `plugin:kizu` must stay one product noun or 9349dc5 goes green again. `cli` vs `core` is the other direction.
- Sibling unpaid does not need the natal *old* token. plugin.json holds `0.3.0` while the natal is `0.6.0→0.7.0`. `is_homonym` was the hole; `bound ≠ old` in `decide_via` was the second latch.
- Default check on 9349dc5 is *one* line. `--explain` still has 28 kin of the word `version` (lien's union). The gate did not become leftover-name.
- sitbone needed no package on `threshold`. Gating every natal by nearest Package.swift would have dropped CLAUDE.md.

## Failures

- No language parser. Japanese bindings still do not parse. Fullwidth `１０` is not `10`.
- Size-cap omit is still silent. Rename-only still mints no natal (DESTROYER_LIEN §3).
- `--explain` generic-version kin flood is inherited. Default check is the object.
- Cargo workspace `[workspace.package]` version vs per-crate version is untested.
- Wrong `-C` is still fail-open (lien §8).

## Suggested mutations

- Path natal (`git mv`) so dest still speaking `t1.py` fails — DESTROYER_LIEN §3, not this package noun.
- CJK as an ident (`タイムアウト = 10`).
- Skip/omit as a line (`omitted=`).
- Default dest = the diff's new side (wrong `-C`).

## Kill / keep

**Keep.** The object changed: natal identity is `(package, noun)`. Workspace homonyms are distinct. kizu `plugin.json` `0.3.0` fails a crate release CI instead of hiding as a homonym. sitbone both-rows still fail. Kill only if a later generation proves `lien` plus a path prefix on `merge_natals` is the same object — it is not: lien's `is_homonym` still drops same-name sibling manifests whose bound value is not the natal old.
