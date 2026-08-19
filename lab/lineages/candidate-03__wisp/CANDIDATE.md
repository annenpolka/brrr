# candidate-03 — wisp

## Primitive

Print the files and symbols that were born and killed between two git refs (invisible in the net diff), then the remnants of those names that still linger at HEAD.

## Why this might not exist

`git diff A B` is the net. `git log A..B` is the commits. The forgotten middle — a parser you tried, a Swift view you added then deleted, a skill plugin that lived for four commits — never appears in the review surface. Remnants of those experiments (comments, aliases, docs that still name the dead type) are a real bug source, especially when an agent "tries something, reverts it, leaves a residue." There is no Unix verb for that interval.

Four primitives considered; the two most conventional were discarded:

1. **tide** — reference-count of a symbol across `git grep` at each commit. A loop around existing tools.
2. **untangle** — partition a dirty tree into independent patches by identifier. A smarter `git add -p`.
3. **wisp** — implemented. Ghosts of the interval plus remnants.
4. **revenant** — classify the current diff as a replay/revert of a historical patch. Kept as a mutation, not this candidate.

## How to run

```bash
chmod +x wisp demo.sh
./wisp --help
./wisp --root                 # whole-repo ghosts
./wisp main HEAD              # branch interval
./wisp --check -q             # CI: exit 1 if remnants
./demo.sh                     # fixture + skills + kizu
```

## Empirical transcript

### Fixture (ugly names, unicode, generated, leftover comments)

```
$ ./wisp --root -C .demo-tmp/haunt --no-color
wisp ∅..main  3 commits

EPHEMERAL FILES (3)  born and died between the refs
  codegen/generated.py
  my file (copy).py
  実験/幽霊.py

EPHEMERAL SYMBOLS (4)
  LegacyParser  class  app.py
  generated_helper  fn  codegen/generated.py
  ghost  fn  実験/幽霊.py
  try_parse_legacy  fn  app.py

REMNANTS (4)  vanished names that still appear at HEAD
  LegacyParser         cmt app.py:4  # used by LegacyParser.try_parse_legacy
  try_parse_legacy     cmt app.py:4  # used by LegacyParser.try_parse_legacy
  幽霊                 cmt app.py:6  # see 幽霊.py leftover
  generated_helper     cmt app.py:7  # generated_helper still documented here
```

`--check` exits 1. Nested git under `nested-lib/` does not crash.

### Real repos, before the first improvement

skills (deleted experiments the net history still "has" only as ghosts):

```
$ ./wisp --root -C skills --files
EPHEMERAL FILES (13)
  preact-zero-mock/SKILL.md                         +007292ad -127df9c4  remove preact-zero-mock
  circuit-breaker/skills/circuit-breaker/SKILL.md   +11716a3f -2d56b11f  remove circuit-breaker plugin
  codebase-investigator/scripts/scout.sh            +b2624c42 -46d867b1  remove scout.sh …
  …
```

sitbone (a UI that was added, then deleted two commits later):

```
$ ./wisp --root -C sitbone --files
EPHEMERAL FILES (1)
  Sources/SitboneUI/FocusRiverView.swift  +14b1d6e3 -70ec7df6
  Clean up: remove unused FocusRiverView + SettingsWindowController
```

kizu v1 was noisy. `--root` on 244 commits: 1 ephemeral file (`deep-research-ai-agent-hooks.md`), 232 symbols, **620 remnants**. Top remnant names were `fake_app` (73), `chars` (64), `span` (48), `take` (22), `head` (16). Most were false positives (see Failures).

voidtrace v1: 251 symbols / 3042 remnants, dominated by types mentioned in `VoidTrace計画.md` and `.pkl` files the definition scanner did not treat as source.

### After the first improvement

Changes: definition regexes are language-scoped (JS `let x =` no longer fires on Swift/Rust); markdown is not mined for defs; `.pkl` counts as source; `as foo` aliases and `let/const` bindings count as *live* names; remnants require CamelCase / long snake_case; names with ≥5 live code hits are dropped as missed aliases; `--check` ignores documentation hits.

kizu 244 commits:

| | v1 | v2 |
| --- | --- | --- |
| symbols | 232 | 35 code + 97 tests |
| remnants | 620 hits / 85 names (`fake_app`, `chars`, `span`, `take`, `head`) | 69 hits / 20 names |
| time | 0.69s | ~0.7s |

Poster-child remnant that v1 drowned and v2 surfaces:

```
is_baseline_path  doc:2
  docs/adr/0007-…:26  `is_baseline_path` 関数廃止 → `BaselineMatcher` struct に置き換え
clean_stale_events  comment:5
  src/app.rs:237      `clean_stale_events`), or
seed_diff_snapshots comment:3
  src/app.rs:6048     `seed_diff_snapshots` keys the map by repo-relative paths
```

sitbone (clean delete, no leftover names):

```
EPHEMERAL FILES (1)
  Sources/SitboneUI/FocusRiverView.swift  +14b1d6e3 -70ec7df6
  Clean up: remove unused FocusRiverView + SettingsWindowController
EPHEMERAL SYMBOLS (9)
  FocusRiverView  struct  Sources/SitboneUI/FocusRiverView.swift
  AppRiverRow     struct  Sources/SitboneUI/FocusRiverView.swift
  NotchBarView / HoverDetector / setupNotch  (earlier UI that also died)
REMNANTS (0)
```

voidtrace: 251 symbols / 3042 remnants → 10 symbols / 0 remnants. The v1 flood was `type DamageAmount` in `VoidTrace計画.md` plus Pkl classes the HEAD scanner skipped. v2 lists real retired operations (`ScaleFixedCritical`, `evaluateFixedMultishotRuntime`).

skills: 13 ephemeral files unchanged (already the right signal). 0 remnants — those plugins were deleted cleanly.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi`
- synthetic fixture in `demo.sh`: spaces in names, Unicode paths, generated file, nested git, leftover comments

## Surprises

- Whole-file add/delete is rare on these repos. Symbol-level ghosts are the common case, except skills (deleted plugin trees) and sitbone (`FocusRiverView.swift`).
- kizu almost never deletes files (`git log --diff-filter=D` is empty for many of these repos) but deletes and renames *functions* constantly.
- A "deleted" name that still has 66 code hits is almost never a remnant — it is a rename/alias the definition regex missed (`app_with_files as fake_app`).

## Failures

1. All language regexes applied to all files. JS `let x = …` fired on Swift/Rust, so `let center =` became an ephemeral "function".
2. Markdown and planning docs were mined for `type`/`struct`/`fn` lines (`DamageAmount` in `VoidTrace計画.md`, tests pasted in `CLAUDE.md`).
3. `.pkl` specs were *not* treated as source, so surviving Pkl classes looked dead and then "remnant-matched" the whole tree.
4. Rust tests without a `test_` prefix flooded the symbol list (`handle_key_ctrl_c_sets_should_quit`).
5. Remnant search treated every leftover token equally; `head`, `take`, `span`, `chars` drowned `is_baseline_path`.
6. `git` default `core.quotepath` octal-escaped Unicode paths (fixed in the prototype before the first commit).
7. First remnant token on a line shadowed others (`LegacyParser.try_parse_legacy` reported only `LegacyParser`) — also fixed pre-commit.

## Suggested mutations

- **revenant mode**: match the working tree *added* lines against historical *deleted* lines (reintroduction detector).
- Function-level snippets of the dead body, not just the signature.
- `--ours` range: `wisp $(git merge-base main HEAD) HEAD` as the default on a feature branch, already approximated.
- Language plugins (tree-sitter) instead of regex.
- `wisp --pick` to restore an ephemeral file from the commit where it last lived.

## Kill / keep

**Keep.** The interval-ghost + remnant pair is a real missing verb. Ephemeral *files* already pay rent on skills and sitbone. After the ranking pass, remnants on kizu are comments and ADRs that still name abolished functions — the thing you actually wanted. `--check` is now plausible on a branch (docs ignored); `--root --check` on a long-lived repo will still fail, which is honest archaeology rather than a CI gate.
