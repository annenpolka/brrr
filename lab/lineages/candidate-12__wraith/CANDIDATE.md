# candidate-12 — wraith

## Primitive

Extract names that lost their last definition in git, then hunt the untyped fringe (docs, configs, scripts, comments, strings) for holdouts a compiler will never see.

You do not supply the old name. Wraith infers the dead identities from history (deleted files, vanished `fn`/`class`/`struct` defs, old path stems) and reports only mentions that remain after the referent is gone.

## Why this might not exist

`rg oldname` works only if you remember `oldname`. `knip` / `ts-prune` / rustc find unused *exports* (defined, never mentioned) or unbound *code* identifiers. The recurring miss is the inverse, in the layers type systems ignore:

- a README table still advertising a deleted skill
- a Makefile / docker-compose volume still pointing at a deleted path
- a kebab-case flag in a shell script after the snake_case function died
- a rustdoc intra-doc link to a method that was extracted away
- an ADR still naming a test that was rewritten

That is a missing Unix verb: *what lingers after it died?*

Four primitives were considered. Discarded as conventional: forgotten change-companions (coupling metrics exist) and unused-export lint. The other odd one was *revenant* (deleted code bodies that later reappear). Wraith was implemented because dogfood targets had almost no file deletions but *did* have leftover names.

## How to run

From this worktree:

```bash
./wraith --self-test
./wraith -C /path/to/repo
./wraith main                     # two-tree vs worktree
./wraith --range main..HEAD --porcelain
./wraith --json --ok-exit
./demo.sh
```

## Empirical transcript

### Before the improvement (v1, commit e766112)

Self-test found the exact leftovers and **missed** the kebab-case echo it was supposed to teach us about:

```
holdout names: ['UserService', 'legacy_jwt_helper', 'legacy_jwt_helper.py',
                'loadLegacyToken', 'retry_with_backoff',
                'src/auth/legacy_jwt_helper.py', 'src/weird name (copy).py',
                'weird name (copy)', 'weird name (copy).py']
required holdouts: ok
known miss (v1): kebab-case leftover 'retry-with-backoff' in scripts/smoke.sh
wraith  9 names linger, 13 mentions
```

Path identities exploded (`legacy_jwt_helper` / `.py` / full path were three holdouts for one docker-compose line). Makefile reported the same line twice.

Real repos:

```
# skills — true positive
$ ./wraith -C .../skills --ok-exit
wraith  1 name linger, 1 mention
preact-zero-mock
  died path  127df9c4  preact-zero-mock/SKILL.md  remove preact-zero-mock
  README.md:15  doc  | **preact-zero-mock** | Preact + HTM でゼロビルドWebモック。…

# kizu — mostly false positives
$ ./wraith -C .../kizu --max-commits 250 --json
deaths 487  dead_names 106  holdouts 64  mentions 299
top: render_diff_line (34), render_diff_line_wrapped (22), render_footer (19)

# sitbone / voidtrace / tenaoshi
sitbone:   deaths 9   dead_names 7   holdouts 0
voidtrace: deaths 14  dead_names 11  holdouts 0
tenaoshi:  deaths 0   dead_names 0   holdouts 0
```

`render_diff_line` was **not dead**. It had moved to `src/ui/diff_line.rs` as `pub(super) fn render_diff_line`. v1's def regex treated `pub` as needing a space, so `pub(crate)` / `pub(super)` / `pub(in path)` were invisible. A file-split looked like a massacre.

### After the improvement

Changes driven by that transcript:

1. Recognize Rust restricted visibility (`pub(crate)`, `pub(super)`, `pub(in …)`).
2. Match kebab / snake / camel / Pascal variants of a dead identifier.
3. Collapse path-identity aliases that only repeat a longer name's mentions.
4. Dedup same-line hits; treat `use x as alias` as a live binding.
5. Do not mine English prose for fake defs; drop variant-only hits that live only in implementation/config (completed rename).
6. `--ignore GLOB` so a planning diary can be subtracted.

Self-test after:

```
holdout names: ['UserService', 'loadLegacyToken', 'retry_with_backoff',
                'src/auth/legacy_jwt_helper.py', 'src/weird name (copy).py']
required holdouts: ok
variant hit: retry-with-backoff
path-identity collapse: ok
wraith  5 names linger, 9 mentions

retry_with_backoff
  Makefile:2  script  … retry_with_backoff …
  scripts/smoke.sh:3  script as retry-with-backoff  retry-with-backoff --times 3
```

Same real repos:

```
# skills — still the one true leftover
$ ./wraith -C .../skills --porcelain --ok-exit
README.md:15:preact-zero-mock:doc:path@127df9c4:preact-zero-mock/SKILL.md

# kizu — false "still exists" names gone
deaths 494  dead_names 38  holdouts 24  mentions 93
# 88 of those mentions are plans/** (the diary of the death)
$ ./wraith -C .../kizu --ignore 'plans/**' --max-commits 250 --ok-exit
wraith  5 names linger, 5 mentions

prev_hunk_last_run_start
  died def  src/app.rs:2532
  src/app/navigation.rs:442  comment
    /// hunk's last run start (via [`Self::prev_hunk_last_run_start`]).

search_jump_next
  src/ui/tests.rs:1815  comment
    // `commit_search_input` and `search_jump_next`/`_prev` both call

# sitbone / voidtrace / tenaoshi stay clean
sitbone:   7 dead names, 0 holdouts
voidtrace: 11 dead names, 0 holdouts
tenaoshi:  0 dead names, 0 holdouts
```

The rustdoc link to `Self::prev_hunk_last_run_start` is the kind of leftover rustc will not flag unless you turn on intra-doc link checking *and* the path still type-checks. Wraith found it because the method died.

## Dogfood targets

| Target | Role |
| --- | --- |
| built-in fixture | rename + deletion + weird filename `src/weird name (copy).py` + leftover Makefile/JSON/compose |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | deleted `preact-zero-mock` still listed in README |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | 244-commit Rust repo, massive file splits |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | deleted `FocusRiverView.swift` — clean removal |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | identifier migrations that look like deaths |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | short history, no deaths |

Read-only. No writes to those trees.

## Surprises

- The highest-value hit was not a function. It was a **directory name** in a markdown table (`preact-zero-mock`). Path identities matter more than AST identities for this primitive.
- kizu's "64 dead functions" were almost all *moved* functions with `pub(super)` visibility. Restricted visibility is how Rust *means* "this is still defined."
- Variant matching, turned on to catch `retry-with-backoff`, immediately invented false positives on voidtrace: `predicateRejected` had become the live string `"predicate-rejected"`. A completed rename is not a holdout.
- `as deterministic` in English prose was parsed as an import alias and "died" when the sentence moved. Def extraction must not run on docs.
- A repo that writes execplans (`kizu/plans/**`) will always mention the dead. That is a diary, not a leak. `--ignore` is the valve.

## Failures

- v1 missed kebab-case leftovers (`retry-with-backoff`).
- v1 treated `pub(super) fn` as deleted; kizu was unusable noise.
- v1 reported the same path death three ways.
- After adding naive `let x =` as a definition, sitbone lit up on `presence` and `counters` (English domain words, still very much alive). Reverted; plain lowercase unpunctuated tokens are no longer distinctive.
- After adding naive `as alias` on all files, voidtrace reported `deterministic` ~100 times. Restricted to code files.
- Two-tree `wraith HEAD~10` on skills found nothing: the deletion is older than 10 commits. History mode is the right default; two-tree needs an old enough left side.
- Nested/merge-commit `--raw` diffs still attribute some deaths to `Merge pull request #N` rather than the feature commit. Cosmetic.
- No attempt to parse generated files specially beyond skip-lists; a generated client from a deleted proto would still look like a holdout (probably correct).

## Suggested mutations

- Intra-doc / rustdoc / typedoc link mode: only report `` [`Name`] `` / `{@link Name}` leftovers.
- CLI-flag deaths: extract `--flags` from `git log -p` on clap/cobra/argparse source, search scripts and README.
- Default `--ignore` for `plans/**`, `CHANGELOG*`, with `--diary` to opt back in.
- `wraith --pr main` as sugar for `--range $(git merge-base main HEAD)..HEAD`.
- Reincarnation sibling: same pipeline, but compare deleted *bodies* (shingles) to new files instead of leftover *names*.
- `--since` + incremental cache of blob fingerprints so a 10k-commit monorepo is cheap.

## Kill / keep

**Keep.** It is a small Unix verb with a grep-shaped interface, it found a real leftover on the first real repo (`skills` README advertising a deleted skill), and after one empirical pass it stopped lying about kizu's module split. The remaining kizu hits outside `plans/` are stale rustdoc and comments pointing at methods that no longer exist — exactly the thing that should already have a command.
