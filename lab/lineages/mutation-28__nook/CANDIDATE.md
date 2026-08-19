# mutation-28 — nook

## Primitive

A protocol token is the **key path** (`pagination.has_more`), not the bare serialized key. Two `has_more` in different objects are different identities and not one leftover. Same path, different inflection (`pagination.has_more` / `pagination.hasMore`) is still a **fork**. Same leaf, different parent is a **homonym**.

## Why this might not exist

`sic` (mutation-01) flipped `aka`’s inflection class into exact wire bytes. That still treats every `"has_more"` as one leftover. A patch that renames `pagination.has_more` is not “done” just because some other object still says `has_more`, and it is not “incomplete” just because `meta.has_more` remains. `rg has_more` and JSON Schema validators cannot say “this slot, not that slot.” jq can address one document. Nobody ships a Unix verb for “this exact path still lives in N files” plus “these two parents share a leaf.”

## How to run

From this worktree:

```bash
./nook --selftest
./nook -C /path/to/repo
./nook -C /path/to/repo pagination.has_more
./nook -C /path/to/repo --homonyms --leaf has_more
./nook -C /path/to/repo --forks
git -C /path/to/repo diff | ./nook --check
./demo.sh
```

Python 3.10+, no extra packages. Exit `0` clean, `1` lookup miss or one-sided check, `130` interrupt.

## Empirical transcript

### Before the improvement (v0.1, first dogfood)

`./nook --selftest` — 37/37 ok. Synthetic fixture (from `./demo.sh`) already worked: `pagination.has_more` and `meta.has_more` listed separately; lookup of one did not include the other’s files; `--homonyms` grouped them; `--forks` paired `pagination.has_more` ~ `pagination.hasMore` and did **not** pair `pagination.has_more` ~ `meta.has_more`; one-sided rename of the pagination slot exited 1 with leftovers `client.ts`, `api.yaml`, `page.json` (not `meta-only.json`); complete pagination rename exited 0 while `meta.has_more` remained.

Real repos:

**tenaoshi** `has_more` split on the first try, which is the flip:

```
HOMONYM  has_more
  has_more              files: 14   # CodingKeys + schema quotes + plan JSON strings
  mock_plan.has_more    files: 8    # EPF-001.json … EPF-008.json
  units[].has_more      files: 1    # EditPlanParserTests.swift (unclosed snippet)
```

`sic has_more` would have reported 22 files as one leftover. `nook mock_plan.has_more` hits only the EPF fixtures. Bare `has_more` does **not** list `EPF-001.json`. That is the bug `sic` cannot see: the plan field and the fixture wrapper are different objects.

But the 14-file unrooted bucket still mixed two *code* objects that share a leaf and nothing else: `WirePlan.has_more` (plan completeness) and `Batch.has_more` (review-batch pagination) both `case hasMore = "has_more"`. `sic` and v0.1 `nook` called them one leftover.

**kizu** the intended hit was not `hook_event_name` (one path, root of the hook payload) but the homonym:

```
HOMONYM  file_path
  tool_input.file_path   files: 6   # Claude/Cursor stdin envelope
  file_path              files: 2   # flattened / quoted
```

and `tool_input.filePath` vs `tool_input.edits[].filePath`. `sic --forks` would have merged `file_path`/`filePath` as one idea. `nook` says they also live in different objects.

Default `--homonyms` led with GitHub Actions `jobs.*.name` / `jobs.*.steps[].name`. Correct paths, unusable report.

**voidtrace** kebab mechanic ids sit at *three* paths:

```
HOMONYM  resolved-beam-ticks
  action.resolved-beam-ticks      files: 6
  mechanics.resolved-beam-ticks   files: 4
  resolved-beam-ticks             files: 3
```

`sic --forks` listed kebab vs snake as one fork. The interesting object is the parent: an `action.*` id is not a `mechanics.*` id. Instance `deltaFromBase` vs `base.deltaFromBase` vs `variants[].deltaFromBase` vs `properties.base.properties.deltaFromBase` (JSON Schema) showed the same pattern. Schema wrappers are a different object, not a synonym.

**sitbone** `lifetimeAwayRecovered` is an unrooted subscript (no parent recovered). Default listing is dotted logger names (`core.session`, `sensors.presence`) because those are quoted protocol strings, not JSON paths. Implicit Codable `awayRecovered` stays invisible — same loss as `sic`.

### After the improvement (v0.2)

Driven by that transcript:

- CodingKeys / serde `rename` take the **enclosing type** as the parent (`WirePlan.has_more` vs `Batch.has_more`). `enum CodingKeys` is skipped so the object, not the adapter enum, is the path prefix.
- Unclosed JSON objects drop their hits (the `units[].has_more` ghost in a sliced parser test).
- `--homonyms` skips boring leaves (`name`, `type`, `path`) unless `--leaf` asked for one; `jobs.*` CI paths sort last.

`./demo.sh` exits 0.

**tenaoshi** `has_more` is now five identities, not one:

```
HOMONYM  has_more
  has_more                         files: 13  # docs, schema required[], plan JSON strings
  mock_plan.has_more               files: 8   # EPF fixtures
  GeneratedEditPlanFixture.has_more files: 2  # OraclesGenerated.swift + spec-gen.ts
  Batch.has_more                   files: 1   # EditPlanInvocationLog.swift:80
  WirePlan.has_more                files: 1   # EditPlan.swift:103
```

`--check` on a rename of `mock_plan.has_more` would leftover other EPF files, not `Batch.has_more`. `sic` would have leftover everything that still said the bytes `has_more`.

**kizu** default `--homonyms` now leads with protocol slots:

```
HOMONYM  filePath
  filePath                    # Cursor dialect
  tool_input.edits[].filePath
  tool_input.filePath
HOMONYM  additionalContext
  additionalContext
  hookSpecificOutput.additionalContext
```

`hookSpecificOutput.additionalContext` vs root `additionalContext` is the stdout envelope vs the flat field — the same class of bug as `pagination` vs `meta`.

**voidtrace** `resolved-beam-ticks` stays three paths. `deltaFromBase` / `metricValue` / `scenarioId` show instance vs schema vs experiment-wrapper as homonyms, not leftovers of each other.

**sitbone** unchanged: no nested JSON persistence. Logger dotted names still list. `t1` CodingKeys would become `Type.t1` when the parent type is visible.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (dirty WIP; not mutated)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- synthetic fixture in `demo.sh`: `pagination` vs `meta` vs `properties`, JSON fork `pagination.hasMore`, unicode path `weird dir/名前.ts`, nested git, `dist/app.min.js`, identifier-only `backgroundColor`

## Surprises

- The interesting object is not the leaf and not the inflection class. It is the **slot**. kizu’s `tool_input.file_path` and flattened `file_path` are a homonym `sic` would have reported as one healthy exact-key pact.
- tenaoshi already writes `case hasMore = "has_more"` on **two** types. `sic` and v0.1 `nook` merged plan-completeness with review-batch pagination. The enclosing type is the parent the JSON document does not write.
- voidtrace’s mechanic id is kebab in three parents (`action`, `mechanics`, bare). That is three contracts, not one leftover and not one fork.
- JSON Schema `properties.X` is a different path from instance `X`. Collapsing schema keywords would be a later mutation, not this one.
- Sitbone’s JSON persistence never writes the key as a literal. Flipping `sic`’s assumption does not recover implicit Codable; it only names the nooks that *are* written.

## Failures

- v0.1 hung on tenaoshi: a JSON array walker treated Swift `[` as JSON and looped. Fixed before the first commit (always-progress + start only at `{` + `"`).
- v0.1 mixed WirePlan and Batch into unrooted `has_more`. Fixed (type prefix).
- v0.1 `units[].has_more` from an unclosed test snippet. Fixed (closed objects only).
- `--homonyms` still has CI / schema-keyword noise (`jobs.ci.runs-on`, `properties.X.minimum`) when you ask `--leaf` or when the leaf is shaped (`runs-on` is kebab). Default ranking now buries `jobs.*`.
- Nested git still needs `--walk` (correct).
- No language parser: comments can still contribute quoted hits; brace counting for type names is string-blind.
- Chained `data.get("pagination").get("has_more")` is not recovered (only `["a"]["b"]`).
- Implicit Codable / serde field names that never appear quoted stay invisible.

## What the flipped assumption bought

- A check that is about **one slot**. A patch that updates `"has_more"` under `pagination` is not dirty because `meta.has_more` remains, and is not clean if another file still speaks `pagination.has_more`.
- `--homonyms`: the dual of `sic --forks`. Two parents of one leaf become a smell instead of a success.
- Type-prefixed adapters: `WirePlan.has_more` ≢ `Batch.has_more`. Header case-fold still holds (`headers.X-Request-Id` ≡ `headers.x-request-id`).
- `--check` on a pagination rename reports leftover **pagination paths**, not leftover `has_more` bytes.

## What it lost

- `sic`’s “every file that still says these bytes” report. That is sometimes what you want for a global find-replace. `nook --leaf has_more` is the recovery hatch, not the default leftover.
- Implicit Codable / serde keys that never appear quoted (sitbone `SessionRecord.awayRecovered`).
- Cross-language rename when one side is only an identifier (Pkl `hasMore = false` vs JSON `"has_more"`). That is `aka`’s job.
- Treating fixture wrapping (`mock_plan.has_more`) as the same leftover as the plan field. Deliberate. They are different objects; migrate them as two paths.

## Suggested mutations

- JSON Schema collapse as an opt-in (`properties.X` → instance `X`) so schema and document can be one leftover when you want that.
- `data.get("pagination").get("has_more")` and `obj.pagination["has_more"]` chains.
- `--strict`: fail `--check` only on leftover code+config, ignore docs.
- Pair with `sic`/`aka`: `nook` for the slot, `sic` for the bytes, `aka` for the adapter inflection.
- Occupancy: which paths did this patch *move* (`pagination.has_more` → `pagination.has_extra`) vs which homonyms it ignored.

## Kill / keep

**Keep.** The verb is the inverse of `sic` the way `sic` was the inverse of `aka`. I/O stays Unix (`git diff | nook --check`). Dogfood found real dual-object `has_more` on tenaoshi (plan vs batch vs fixture), `tool_input.file_path` vs `file_path` on kizu, and three-parent mechanic ids on voidtrace — without identifier false positives and without treating a sibling `has_more` as leftover. Not a flag on `sic`.
