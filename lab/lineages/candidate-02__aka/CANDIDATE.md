# candidate-02 — aka

## Primitive

Treat a protocol token as one identity across naming inflections (`has_more` / `hasMore` / `HAS_MORE` / `has-more`) and fail a patch that updates only some of its files.

## Why this might not exist

`rg has_more` misses `hasMore`. Language servers track one rename in one language. i18n checkers track one catalog. Nobody ships a Unix verb for the implicit ABI that already lives in the repo: the same wire field spelled three ways across spec, Swift, TypeScript, and a JSON schema.

Same-commit co-change and “grep the deleted name” were discarded as conventional. The other leftover idea was lagged file pairing (`also`); `aka` is the weirder one.

## How to run

From this worktree:

```bash
./aka --selftest
./aka -C /path/to/repo
./aka -C /path/to/repo has_more
git -C /path/to/repo diff | ./aka --check
./demo.sh
```

Python 3.10+, no extra packages. Exit `0` clean, `1` lookup miss or one-sided check, `130` interrupt.

## Empirical transcript

### Before the improvement (v0.1, first dogfood)

`./aka --selftest` — 16/16 ok.

Synthetic fixture (from `./demo.sh`) already worked: `has.more` joined `has_more` + `hasMore`; one-sided rename of the producer exited 1 with leftovers `src/client.ts`, `spec/api.yaml`; updating both leftovers exited 0.

Real repos were useful and noisy.

tenaoshi top hits included the real pact:

```
has.more  forms: hasMore, has_more  files: 11  layers: code,doc,other,test
  AGENTS.md:26  ident  has_more
  Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift:54  ident  hasMore
  Shell/Sources/Tenaoshi/PanelSession.swift:430  ident  hasMore
  docs/SPEC.md:88  ident  has_more
  specs/tenaoshi.pkl:33  ident  hasMore
```

…but also `tenaoshi.engine.tests` with a single form `TenaoshiEngineTests`, and `source.text` almost died on `--max-files 14`. Every quoted `"has_more"` was double-counted as `ident` because identifier scan walked inside strings. `spec/api.yaml` was tagged `test` because `/spec/` was a test-path hint. `unicode_escape` on real Swift/regex strings dumped DeprecationWarning storms. `aka --porcelain TOKEN | grep` raised `BrokenPipeError`. `--check` on tenaoshi’s already-dirty tree emitted identifier junk (`backgroundColor`, `provider`, `refinements`).

kizu `--code` mixed real pacts (`hook.event.name` = `hookEventName`/`hook_event_name`, `hook.log.event` = `HookLogEvent`/`hook-log-event`) with single-form clones (`MultiEdit`).

### After the improvement (v0.2)

Changes driven by that transcript:

- do not extract identifiers inside string literals
- default list requires two or more surface forms
- skip `*Generated.*` (tenaoshi oracles)
- `/spec/` is not a test directory; `.html` is doc
- `--check` only on pacts with a wire witness (lit/key/flag); ident-only names are ordinary code
- ignore generated files inside the patch
- broken-pipe safe; no `unicode_escape`

`./demo.sh` still exits 0. tenaoshi list is now inflection-only, no `OraclesGenerated.swift`, no `TenaoshiEngineTests` pact:

```
has.more  forms: hasMore, has_more  files: 10  layers: code,doc
  AGENTS.md:26  ident  has_more
  Shell/Sources/Tenaoshi/PanelSession.swift:430  ident  hasMore
  contracts/rules.md:31  ident  has_more
  docs/SPEC.md:88  ident  has_more
  specs/tenaoshi.pkl:33  ident  hasMore
  tools/spec-gen.ts:39  ident  hasMore
```

kizu `--code` top pacts are all multi-form: `KIZU_BIN`/`kizu_bin`, `ClaudeCode`/`claude-code`, `hookEventName`/`hook_event_name`, `BG_ADDED`/`bg_added`, `HookLogEvent`/`hook-log-event`.

voidtrace (not in the first pass) is the sharpest hit — four spellings of one mechanic id:

```
resolved.beam.ticks  forms: ResolvedBeamTicks, resolved-beam-ticks, resolvedBeamTicks, resolved_beam_ticks  files: 8
  packages/kernel/src/evaluate.ts:2215          lit    resolved-beam-ticks
  specs/golden/resolved-beam-ticks.pkl:2        ident  resolvedBeamTicks
  specs/mechanics/clauses.pkl:116               ident  ResolvedBeamTicks
  specs/patterns/base.pkl:139                   lit    resolved_beam_ticks
  tools/spec-gen/src/model.ts:22                lit    resolved_beam_ticks
```

`--check` on tenaoshi’s pre-existing dirty spec rewrite (read-only; we did not touch that tree) collapsed from a flood of ident splits to 14 protocol leftovers, including `default.provider`, `source.app`, `context.after`, `custom.intents`. That matches a half-migrated spec: docs moved, Swift/pkl still speak the old inflection.

One-sided fixture still fails exactly as designed:

```
SPLIT  has.more
  changed:   src/server.py
  leftover:  spec/api.yaml, src/client.ts
  still as:  hasMore, has_more
```

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (dirty WIP; not mutated)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills`
- synthetic fixture in `demo.sh`: unicode path `weird dir/名前.ts`, nested git, `dist/app.min.js`, single-form `MultiEdit` clone

## Surprises

- The interesting object is not the string. It is the *inflection class*. voidtrace’s `resolved-beam-ticks` vs `resolved_beam_ticks` vs `ResolvedBeamTicks` is one contract living in pkl, TS, JSON Schema, and markdown.
- tenaoshi already writes `case hasMore = "has_more"` in Swift. `aka` still helps because the spec, prompt, HTML mock, and generator keep their own spellings.
- `--check` on a large dirty rewrite is a “what did this WIP orphan?” report, not just a pre-commit nanny.

## Failures

- First `--check` on tenaoshi: ident-only false positives (`backgroundColor`, `provider`). Fixed by requiring a wire witness.
- `unicode_escape` warnings / possible UTF-8 corruption on real sources. Fixed.
- `BrokenPipeError` under `aka --porcelain | grep -q`. Fixed.
- `/spec/` marked OpenAPI-style dirs as tests. Fixed.
- Generated oracles drowned tenaoshi. Now skipped.
- Nested git is invisible to `git ls-files` (correct). `--walk` sees it; documented in demo.
- `ins.bg` (`ins-bg` CSS class in a mock) is a weak pact. Still leftover noise.
- skills `input_summary` is a single form (clone, not cognate). Lookup works; default list hides it unless `--min-forms 1`.
- No language parser: comments still contribute identifier hits.

## Suggested mutations

- Tag a file that contains *both* forms as an adapter (`CodingKeys`) and down-rank it.
- `--touched`: default to pacts intersecting the current diff.
- Historical `aka`: stitch git-rename commits into the alias graph.
- Tree-sitter / comment-aware extractors.
- Pair with lagged file coupling (`also`): “you changed `hasMore` here; historically `spec-gen.ts` follows.”
- `--strict` leftover policy: ignore docs-only leftovers, or only fail on code+config leftovers.

## Kill / keep

**Keep.** The verb is new, the I/O is Unix (`git diff | aka --check`), and it found real cross-inflection contracts on four independent repos plus a dirty spec migration. Not a wrapper around `rg` or `git log`.
