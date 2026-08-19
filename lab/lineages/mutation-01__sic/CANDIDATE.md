# mutation-01 — sic

## Primitive

A protocol token is the **exact serialized wire key** (JSON/YAML/TOML key, HTTP header name, quoted protocol string). Code identifiers are invisible. Inflection neighbors (`has_more` / `hasMore`) are a **fork**, not one identity. `--check` fails a patch that updates that exact spelling on only some of its files.

## Why this might not exist

`aka` (candidate-02) treated a token as an identifier inflection class. That merges the adapter (`case hasMore = "has_more"`) with the wire (`"has_more"`) and cannot see the bug it hides: two *different* bytes on the wire that look like the same field. `rg has_more` misses YAML `has_more:` vs JSON `"hasMore"` as a *pair of contracts*. JSON Schema validators check one schema. Nobody ships a Unix verb for “these exact bytes still live in N files” plus “these two spellings are both on the wire.”

## How to run

From this worktree:

```bash
./sic --selftest
./sic -C /path/to/repo
./sic -C /path/to/repo has_more
./sic -C /path/to/repo --forks
git -C /path/to/repo diff | ./sic --check
./demo.sh
```

Python 3.10+, no extra packages. Exit `0` clean, `1` lookup miss or one-sided check, `130` interrupt.

## Empirical transcript

### Before the improvement (v0.1, first dogfood)

`./sic --selftest` — 32/32 ok. Synthetic fixture (from `./demo.sh`) already worked: `has_more` stayed exact; `hasMore` as a JSON key was a different token and a `FORK`; identifier `hasMore` / `backgroundColor` never appeared; one-sided rename of `"has_more"` exited 1 with leftovers `src/client.ts`, `spec/api.yaml` (not `spec/legacy.json`, which speaks `hasMore`); complete exact-key rename exited 0.

Real repos:

**tenaoshi** `has_more` was only 5 git-tracked docs/test files. The dirty WIP’s real witnesses — `EditPlan.swift` `case hasMore = "has_more"`, `contracts/testcases/EPF-*.json` `"has_more":` — were untracked, so `git ls-files` hid them. `sic hasMore` correctly missed (identifier only) and hinted `wire forks: has_more`. `--forks` was empty: the wire has one spelling.

**kizu** `hook_event_name` (stdin JSON) vs `hookEventName` (stdout JSON) was the intended hit. `--forks` also surfaced `file_path`/`filePath` and `additional_context`/`additionalContext` — three real multi-agent wire dialects. Noise: Pascal backticks (`DiffLine`), `App.files` vs `app.files`.

**voidtrace** kebab `"resolved-beam-ticks"` (kernel action kind) vs snake `"resolved_beam_ticks"` (pkl pattern / generated manifest) listed as a fork. Default list was useful kebab event ids (`event.critical-tier`, `action.multishot-direct-hit`).

**sitbone** failed the first demo: `lifetimeAwayRecovered` is `dict["lifetimeAwayRecovered"]` in Swift. `STRING_RE` paired a leftover `"` from an earlier `dict["…"]` with the next one, swallowing the key. CodingKeys `= "t1"` was dropped (length 2). Listing led with `YouTube` (Pascal quoted site names) and `yyyy-MM-dd` misread as an HTTP header.

### After the improvement (v0.2)

Driven by that transcript:

- index untracked non-ignored files (`git ls-files -co --exclude-standard`)
- dedicated `dict["key"]` / `.get("key")` / `= "raw"` extractors (CodingKeys, serde rename, Swift subscripts)
- double quotes only in Swift/TS/JSON so apostrophes cannot swallow keys
- header identity requires `X-*`, a well-known name, or title-case segments (`yyyy-MM-dd` is not a header)
- drop Pascal product names from quoted witnesses; keep them only as JSON object keys
- `--forks` requires snake/kebab/camel/const or a structured (json/yaml/toml/header) witness

`./demo.sh` exits 0.

**tenaoshi** `has_more` is now 22 files, including the adapter raw value and the JSON fixtures:

```
has_more  files: 22  kinds: json,quoted  layers: code,config,doc,test
  Engine/Sources/TenaoshiEngine/EditPlan.swift:103          quoted
  Engine/Sources/TenaoshiEngine/EditPlanOutputSchema.swift:29 json
  contracts/testcases/EPF-001.json:10                       json
```

`sic hasMore` → exit 1, `wire forks: has_more`. `--forks` still empty: this repo’s wire is one spelling. `--check` on the dirty spec rewrite reports **10 exact-key splits**, all real protocol leftovers, no identifier junk:

```
SPLIT  context_after
  changed:   OraclesGenerated.swift, tools/spec-gen.ts
  leftover:  EditPlanInvocationLog.swift, InvocationLog.swift, EPC-*.json, EPF-*.json, …
SPLIT  source_app / input_text / latency_ms / context_before / …
```

**kizu** forks that matter:

```
FORK  hook.event.name
  hook_event_name   files: 6   kinds: json    # Claude/Cursor/Codex stdin
  hookEventName     files: 2   kinds: json    # Claude stdout envelope
FORK  file.path
  file_path         files: 8   kinds: json,quoted
  filePath          files: 2   kinds: json,quoted   # Cursor
FORK  additional.context
  additionalContext files: 9   kinds: json,quoted   # Claude/Codex
  additional_context files: 3  kinds: json,quoted   # Cursor
```

**voidtrace**:

```
FORK  resolved.beam.ticks
  resolved_beam_ticks   files: 5   # pkl pattern + generated manifest
  resolved-beam-ticks   files: 3   # kernel action kind
```

**sitbone** `lifetimeAwayRecovered` is the subscript on `SitboneCore.swift:1048`. `t1` is the CodingKeys raw value. `YouTube` / `yyyy-MM-dd` gone from the default list. Docs still fork `away_recovered` (SPEC.md) vs `awayRecovered` (ADR) — the JSON Codable field itself is an unquoted identifier and stays invisible.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (dirty WIP; not mutated)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone`
- synthetic fixture in `demo.sh`: unicode path `weird dir/名前.ts`, nested git, `dist/app.min.js`, identifier-only `backgroundColor`, JSON fork `hasMore`

## Surprises

- The interesting object is not the inflection class. It is the **bytes on the wire**. kizu’s stdin key `hook_event_name` and stdout key `hookEventName` are a protocol fork `aka` would have merged into one “healthy” pact.
- tenaoshi already writes `case hasMore = "has_more"`. `sic` keeps the quoted raw value and drops the identifier. `--check` then reports the half-migrated *wire* (`context_after` still in EPC fixtures after oracles dropped it), not `backgroundColor`.
- voidtrace’s mechanic id is kebab in the kernel and snake in the generated spec manifest. That is a serialization bug, not a cognate.
- Sitbone’s JSON persistence never writes the key as a literal (`awayRecovered` is implicit Codable). Flipping the assumption makes that contract disappear. The leftover signal is the doc fork `away_recovered` ~ `awayRecovered`.

## Failures

- v0.1 missed untracked tenaoshi fixtures. Fixed (`ls-files -co`).
- v0.1 Swift `dict["key"]` quote pairing. Fixed (subscript extractor + no single-quoted strings in Swift).
- v0.1 `yyyy-MM-dd` as a header; `YouTube` as a token. Fixed (title-case headers; no Pascal quoted witnesses).
- `--forks` still has weak pairs (`handle_key` ~ `handle_key_`, `kizu-e2e` ~ `kizu-e2e-`, Cargo `dev-dependencies` vs npm `devDependencies`). The last one is arguably real.
- `stop.fill` (SF Symbol) ranks on sitbone because it is a dotted quoted string in two UI files.
- Nested git still needs `--walk` (correct).
- No language parser: comments can still contribute quoted hits.

## What the flipped assumption bought

- A check that is about **one serialized name**, so a patch that updates `"has_more"` is not “done” just because `hasMore` identifiers moved.
- `--forks`: the dual of `aka`. Two wire spellings of one idea become a smell instead of a success.
- Header case-fold without camel/snake fold. `X-Request-Id` ≡ `x-request-id`; `has_more` ≢ `hasMore`.
- `--check` on a dirty spec rewrite reports leftover **JSON keys**, not leftover Swift properties.

## What it lost

- Implicit Codable / serde keys that never appear quoted (sitbone `SessionRecord.awayRecovered`).
- Cross-language rename detection when one side is only an identifier (Pkl `hasMore = false` vs JSON `"has_more"`). That is `aka`’s job; `sic` will not see the Pkl field at all.
- Single-form identifier clones (`backgroundColor` in two Swift files) — deliberately. They are not a wire contract.

## Suggested mutations

- Recover implicit Codable/serde keys only when a type is `Codable` / `Serialize` and has no `CodingKeys` — a narrow, language-aware exception, not a return to identifier mining.
- Key-*path* identity (`pagination.has_more` vs `meta.has_more`).
- `--strict`: fail `--check` only on leftover code+config, ignore docs.
- OpenAPI `required: [has_more]` and JSON Schema `properties` as first-class key witnesses.
- Pair with `aka`: `sic` for the wire, `aka` for adapters that *translate* the wire.

## Kill / keep

**Keep.** The verb is the inverse of `aka`, the I/O is Unix (`git diff | sic --check`), and dogfood found real dual-serialization on kizu and voidtrace plus a 10-key leftover report on tenaoshi’s dirty spec migration — without identifier false positives. Not a flag on `aka`.
