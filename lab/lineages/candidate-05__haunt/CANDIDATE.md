# candidate-05 — haunt

## Primitive

Mine git deletions of definitions (functions, types, flags, paths) and report the ones the *living* tree still talks about — the inverse of dead-code detection.

## Why this might not exist

Dead-code tools (`knip`, `vulture`, `unimported`) find living symbols with no references. Developers grepping after a rename ask a different question: *which old names did we forget to stop saying?* That requires joining history (what died) to the present (what is still uttered), then splitting obituaries (changelog, ExecPlans, ADRs) from leftovers (README, tests, CI, source comments). `git log -S` + `rg` is the manual workflow; nobody packaged the join as a Unix verb.

Privately considered and discarded as too conventional: (1) co-change hitchhikers / Code Maat logical coupling; (2) stale markdown link checkers. The other non-conventional primitive not built this round: `whittle` — hierarchical delta-debug of a tree or a diff against a command to find the load-bearing file set.

## How to run

```bash
chmod +x ./haunt
./haunt --self-test
./demo.sh
./haunt -C /path/to/repo
./haunt -C /path/to/repo --json --strict
./haunt -C /path/to/repo --archival   # also print names that linger only in plans/ADRs
```

## Empirical transcript

### v0.1.0 — first working software (commit 61c1258)

```
$ ./haunt --self-test
self-test ok
```

```
$ ./haunt -C …/skills --tsv -v
scanned 49 commits, 26 unique deaths
3 haunts, 23 dead, 0 moves
HAUNT  file  circuit-breaker/skills/circuit-breaker/SKILL.md   # false: basename SKILL.md
HAUNT  file  preact-zero-mock/SKILL.md                         # false: basename SKILL.md
HAUNT  file  circuit-breaker/scripts/init.sh                   # false: basename init.sh
```

```
$ ./haunt -C …/tenaoshi -v
scanned 18 commits, 0 unique deaths
0 haunts
```

```
$ ./haunt -C …/sitbone -v
scanned 93 commits, 27 unique deaths
0 haunts, 19 dead, 8 moves
```

```
$ ./haunt -C …/kizu -v
scanned 226 commits, 639 unique deaths
38 haunts, 98 dead, 503 moves
HAUNT  fn    fake_app              # living alias: app_with_files as fake_app
HAUNT  flag  porcelain             # still passed as --porcelain=v1
HAUNT  flag  non-interactive       # still a clap --non-interactive
HAUNT  enum  WatcherHealth         # kind-shifted to struct WatcherHealth
HAUNT  fn    kizu_bin
HAUNT  struct FileViewVisualIndex  # only in plans/
HAUNT  flag  scope                 # extracted from a plan file, still a live flag
…
```

```
$ ./haunt -C …/voidtrace -v
scanned 78 commits, 52 unique deaths
1 haunts, 14 dead, 37 moves
HAUNT  fn  predicateRejected       # test local const, not a call of the deleted fn
```

### v0.2.0 — after dogfood (this commit)

Fixes from the failures above: unique-basename path matching; kind-shift and `as` aliases count as MOVE; live `--flag` / clap `#[arg(long)]` detection; do not mine definitions from markdown/plans; ARCHIVE vs HAUNT; require call/backtick for fn remnants in code; ignore rename-destination substring hits.

```
$ ./haunt --self-test
self-test ok
```

```
$ ./haunt -C …/skills -v
scanned 49 commits, 26 unique deaths
0 haunts, 0 archival, 26 dead, 0 moves
no haunts
```

```
$ ./haunt -C …/tenaoshi -v
0 haunts
```

```
$ ./haunt -C …/sitbone -v
0 haunts, 19 dead, 8 moves
```

```
$ ./haunt -C …/voidtrace -v
0 haunts, 15 dead, 37 moves
```

```
$ ./haunt -C …/kizu -v
scanned 226 commits, 637 unique deaths
6 haunts, 26 archival, 99 dead, 506 moves
HAUNT  fn     clean_stale_events     # leftover comments after the fn was removed
HAUNT  struct BaselineMatcher        # leftover comment; type is now BaselineMatcherInner
HAUNT  fn     kizu_bin               # leftover docs/comments after fn → kizu_bin_for_scope
HAUNT  fn     seed_diff_snapshots    # leftover comments after rename
HAUNT  fn     scope_incompatible     # docs still say "current scope_incompatible"; src has zero hits
HAUNT  fn     search_jump_next       # leftover test comment after thin wrappers were deleted
```

kizu 38 → 6 operational haunts. The 26 ARCHIVE hits are ExecPlan/ADR mentions of deleted tests (`compute_diff_caps_untracked_file_at_read_limit`, …) — historical record, shown only with `--archival`.

Synthetic ugly fixture (spaces in filenames, nested git, generated files skipped) still reports `parse_legacy_widget`, `--legacy-widget`, `odd_name_helper`, `scripts/deploy_legacy.sh`.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/skills`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`
- synthetic fixture with spaces in filenames, nested git, generated files (`demo.sh`, `--self-test`)

## Surprises

- sitbone is historically “clean”: deletions happened, mentions did not linger.
- tenaoshi’s 18 commits contain no deleted definitions the scanner recognizes (all additive / Swift that never lost a `func` line).
- kizu’s `plans/` and `docs/adr/` are a graveyard of old names *on purpose* — archival mentions dwarf operational leftovers (~26 vs 6 after the split).
- `enum WatcherHealth` “died” and immediately became `struct WatcherHealth` — same name, new kind; treating that as HAUNT was wrong.
- Git rename `deep-research-ai-agent-hooks.md` → `docs/deep-research-ai-agent-hooks.md` made every new-path mention look like an old-path leftover because the old name is a suffix of the new one.

## Failures

v0.1 false positives from first dogfood (addressed in v0.2):

1. **Generic basenames.** Deleted `SKILL.md` / `init.sh` matched every remaining file with that basename.
2. **Kind shift.** `WatcherHealth` enum → struct still defined.
3. **Aliases.** `app_with_files as fake_app` is a living alias.
4. **Live flags.** `--scope`, `--porcelain`, `--non-interactive` still exist in clap/argv; v0.1 only treated quoted/`long =` forms as definitions, and mined flags from plan markdown.
5. **Archival remnants.** ExecPlans and ADRs talking about deleted tests looked like haunts.
6. **Homonym locals.** voidtrace `predicateRejected` lives on as a test `const`, not the deleted function.
7. **Rename substring.** (found on second dogfood) new path contains old basename.

Remaining noise: `kizu_bin` as a leftover *parameter* name after the *function* `fn kizu_bin()` died — a homonym the call/backtick heuristic still accepts because comments write `` `kizu_bin` ``.

## Suggested mutations

- Parse `#[arg(long)] field_name` more broadly (already does a first cut) and cobra/clap builders.
- `--blame-remnant`: who last touched the leftover line.
- Language plugins (tree-sitter) instead of regex defs.
- Inverse mode: living defs never mentioned (classical dead code) as a twin stream.
- Treat parameter names / locals as living defs so `kizu_bin` is MOVE.
- `haunt --fix` that comments `// haunt: name died in abc123` on remnant lines (too spicy?).

## Kill / keep

**Keep.** The inverse-of-dead-code join is a real missing verb. First dogfood produced a sharp false-positive taxonomy; second pass cut kizu 38→6 and zeroed skills/voidtrace false hits while keeping true leftovers (`scope_incompatible` documented as current but absent from `src/`). Kill only if a later generation cannot beat regex identity (tree-sitter) — the *interaction* should survive a reimplementation.
