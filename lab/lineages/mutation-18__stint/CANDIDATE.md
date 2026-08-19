# mutation-18 — stint

## Primitive

Interval occupancy of files and symbols that were born and killed between two git refs, plus `--pick` of the last blob. No leftover-name search.

## Why this might not exist

`wisp` (candidate-03) paired interval ghosts with remnant-name search. A critic killed the remnant half as a worse `wraith`. What remained was treated as a list of vanished paths.

The missed object is **occupancy**. `git log -- PATH` does not answer "how many commits did this hold the tree, and what was the last body?" `held exists PATH` answers it only if you already know the path. `git checkout DELETE^ -- PATH` restores it only if you already know the death. The recurring verb is: *what occupied this interval invisibly in the net diff, and give me the last tree.*

`--pick` is recover-lost-work for an ephemeral path. Remnants are `wraith`'s job.

## How to run

```bash
chmod +x stint demo.sh
./stint --help
./stint --root
./stint --root --pick FocusRiverView.swift
./stint --root --pick circuit-breaker/ --to /tmp/out
./stint --check -q
./demo.sh
```

## Empirical transcript

### Fixture (spaces, unicode, two spans, last-blob pick)

```
$ ./stint --root -C .demo-tmp/haunt --no-color
stint ∅..main  6 commits

EPHEMERAL FILES (5)  occupied the interval, gone at both ends
  実験/幽霊.py
    occupied 3  …  2 spans  27B
    +… -…  delete unicode ghost again
  plugin/detect.sh
    occupied 2  …  23B  blob 4ed4592e
```

`--pick detect.sh` prints the *second* body (`v2-last`), not the add. `--pick 幽霊.py` prints the second occupancy (`return 99`). JSON has no `remnants` key. `--check` exits 1.

### Real repos, before the first improvement

skills (deleted experiments; occupancy ranks what wisp only dated):

```
$ ./stint --root -C skills --files
EPHEMERAL FILES (13)
  preact-zero-mock/SKILL.md                         occupied 31  7.1K
  preact-zero-mock/template/*                       occupied 31
  circuit-breaker/skills/circuit-breaker/SKILL.md   occupied 6   3.2K  blob de055581
  circuit-breaker/scripts/detect.sh                 occupied 6   2.3K
  circuit-breaker/scripts/score.jq                  occupied 5   4.5K  (born one commit later)
  codebase-investigator/scripts/scout.sh            occupied 1   9.6K
```

`--pick circuit-breaker/skills/circuit-breaker/SKILL.md` restores blob `de055581` (3249 bytes), last occupied at `e0ad330` ("simplify gating"), died at `2d56b11` ("remove circuit-breaker plugin"). 0.10s.

sitbone (the file that lived 11 commits, then a cleanup):

```
$ ./stint --root -C sitbone
EPHEMERAL FILES (1)
  Sources/SitboneUI/FocusRiverView.swift
    occupied 11  14b1d6e3..1fefafbc  7.5K  blob ee93cacd
    +14b1d6e3 -70ec7df6  Clean up: remove unused FocusRiverView + SettingsWindowController

EPHEMERAL SYMBOLS
  AppClassification / AppRiverRow / FocusRiverView / SettingsWindowController / sampleApps
    occupied 11  (same death)
  toggleBtn  occupied 36
  HoverDetector / CompactRiverRow  occupied 5
```

`--pick FocusRiverView.swift` (basename) restores 7698 bytes containing `public struct FocusRiverView`. Occupancy 11 matches `held --full exists` on the same path, without naming the path first. 0.17s.

kizu 244 commits: **0 ephemeral files**, 38 symbols (`fake_app` occupied 191 — a rename, not an experiment). File grain is the honest empty set; symbol occupancy still inherits wisp's missed-alias noise.

### After the first improvement (v0.2: tree pick + death cohorts)

Dogfood said the unit of recovery is the *experiment*, not one path. v0.1 rejected `--pick circuit-breaker/` as ambiguous (6 files). v0.2 treats a prefix as a deleted tree.

```
$ ./stint --root -C skills --files
EPHEMERAL FILES (13)
  COHORT -127df9c4  remove preact-zero-mock  (6 files, occupied 31)
  COHORT -2d56b11f  remove circuit-breaker plugin  (6 files, occupied 5–6)
    … SKILL.md occupied 6  3.2K
    … score.jq occupied 5  4.5K   ← born in the rebuild, shorter stint
  COHORT -46d867b1  remove scout.sh …  (1 file, occupied 1)
```

```
$ ./stint --root -C skills --pick circuit-breaker/ --to /tmp/cb
# 6 last blobs: SKILL.md de055581 3249B, score.jq 17a3483e 4590B, detect.sh, init.sh, hooks, plugin.json
```

`--pick preact-zero-mock/` restores that 31-commit template tree (6 blobs). sitbone still has one file, so no cohort header; `--pick FocusRiverView.swift` is unchanged (7698B, occupied 11).

`./demo.sh` exit 0, including fixture `--pick plugin/` (detect.sh last body `v2-last` + init.sh).

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — circuit-breaker plugin tree
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView.swift
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — negative: almost no deleted files
- synthetic fixture in `demo.sh`: spaces, Unicode, two occupancy spans, last-blob pick, `--pick plugin/` tree, nested git

## Surprises

- Sibling files in one deleted plugin have **different occupancy**. `score.jq` was born in the rebuild commit; the rest of circuit-breaker occupied one more commit. wisp's `+born -died` hid that.
- `preact-zero-mock` occupied 31 of 49 skills commits — the long experiment. Occupancy sort puts it first; birth-time sort would not tell you it was the durable one.
- sitbone occupancy 11 equals `held`'s TRUE era. stint *discovers* the path; held *requires* it.

## Failures

1. `git log --raw` abbreviates blob ids; first size pass reported `0B` until `--no-abbrev`.
2. kizu symbols with occupancy 191/244 are renames, not stints. No leftover-name search means we cannot apply wisp's "many live hits ⇒ alias" filter.
3. Multi-file `--pick` without `--to`/`--write` still errors (concatenating blobs to stdout is not a tree). Honest, but you have to remember the flag.

## Suggested mutations

- Occupancy-fraction filter for symbols (drop defs that held most of the interval).
- `--pick` of a symbol emits the last defining snippet.
- `--pick --write` as a 3-way with the working tree if the path was reintroduced dirty.

## Kill / keep

**Keep.** The critic was right to kill remnants (that is wraith). Occupancy + last blob + tree pick is a different verb from wisp's born/died list and from held's named-predicate eras. skills pays rent twice: ranking (preact 31 vs circuit-breaker 6 vs scout 1) and `--pick circuit-breaker/` restoring the plugin. sitbone `FocusRiverView` occupancy 11 matches `held` without naming the path first.
