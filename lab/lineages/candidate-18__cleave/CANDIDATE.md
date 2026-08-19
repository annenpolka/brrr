# candidate-18 — cleave

## Primitive

A function is the set of **argument worlds** its callers inhabit. `cleave` partitions call sites by observed arguments (literal / default / dynamic / collection member), then reports when tests and production do not live in the same worlds.

## Why this might not exist

Coverage is a boolean per line. `grep fn(` is a flat list of sites. Mutation testing asks whether an assertion would catch a change. None of them ask the daily question: *the tests call `isBrowser("Chrome")`; production calls `isBrowser(currentApp)` — do they even inhabit the same function?*

The missing Unix verb is a **test/prod inhabitance join on argument shape**, not another linter and not a coverage number.

Four primitives considered:

1. `ritual` — sequential co-call mining. Discarded as conventional (API-protocol mining).
2. `whytest` — static test-impact from a diff. Discarded as conventional (named-gap hunk-to-tests).
3. `seep` — ldd for side effects through the call graph. Unusual; leftover mutation.
4. `cleave` — argument-world inhabitance. Implemented.

## How to run

```bash
./cleave --help
./demo.sh
./cleave --self-test
./cleave -C fixtures/ugly connect
./cleave -C /path/to/repo --check --porcelain
./cleave -C /path/to/repo --json isBrowser
```

Exit 0 on success. `--check` exits 1 if any function tilts. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1, commit 8c9df52)

Ugly fixture already worked. Real repos, 2026-08-20:

```
sitbone    files=49  defs=409  calls=3072  tilt_fns=24  tilts=51
kizu       files=70  defs=931  calls=10327 tilt_fns=37  tilts=75
voidtrace  files=86  defs=598  calls=12260 tilt_fns=64  tilts=342
tenaoshi   files=25  defs=170  calls=1599  tilt_fns=0   tilts=0
skills     files=2   defs=12   calls=143   tilt_fns=0   tilts=0
stratal    files=0   (empty tree)
```

sitbone `isBrowser` was already the right *question*:

```
WindowTitleParser.isBrowser  …  TILT
  world  {appName="Google Chrome"}  test:2
  world  {appName=*}                prod:2
  tilt   prod-open  appName  tests=["Arc","Firefox","Google Chrome","Safari","Terminal"]  prod=*
```

Tests pass string literals; production passes `currentApp`. Envelope truncated at 5 (VS Code dropped). The production set in `browsers: Set<String>` (Brave, Edge, Opera, Vivaldi, Chromium, Orion) was invisible — `contains(appName)` is not `==`.

### v0.1 failures on real queries

1. **`Tests/` was not a test path.** Regex listed `tests` but not `Tests`. tenaoshi's `Engine/Tests/…/OraclesGenerated.swift` was classified as production, so every call was "prod" and **tilt_fns=0**. sitbone escaped only because `WindowTitleParserTests.swift` matches `Tests.swift$`.
2. **Test helpers became subjects.** voidtrace `artifactRef` (defined in `validator.test.ts`) produced 187 of 342 tilts — one `test-only-const` per fixture id. kizu `src/test_support.rs` (`single_added_hunk_file`, `prefixed_diff_lines`) dominated the porcelain; `run_split_command` was buried.
3. **Swift type name was the last protocol.** `public final class SiteObserver: @unchecked Sendable` reported as `Sendable.record`. `CumulativeRecord: Equatable` reported as `Equatable.accumulate`. `Codable.encode` was a stdlib ghost.
4. **One tilt row per literal.** `SiteObserver.record` emitted nine `test-only-const duration=N` lines.
5. **No collection envelope.** `browsers.contains(appName)` never became an arm, so sitbone's real hole (six untested browser names) was silent.
6. **Interpolated XCTest strings leaked as arguments.** `site="expected .activityRecovered, got \(String(des…"`.
7. **`extractSiteName` has zero production calls.** Confirmed with `rg`: only the definition and `WindowTitleParserTests.swift`. Not a parser miss — the public API is test-only. Production uses `SiteResolver`.

### After the improvement (v0.2)

Fixes: case-insensitive `Tests/`; skip test-path / `test_support` defs as subjects (`--test-defs` to include); type name is the first ident after `class`/`struct`/`enum`/`actor` (Rust `impl Trait for Type` still takes Type); collapse per-param value lists; collection membership (`contains` / `in`); interpolated strings are dynamic.

```
sitbone    tilt_fns=24→23  tilts=51→38
kizu       tilt_fns=37→29  tilts=75→41
voidtrace  tilt_fns=64→56  tilts=342→95
tenaoshi   tilt_fns=0→4    tilts=0→4     # Tests/ classification
```

sitbone `isBrowser` after:

```
WindowTitleParser.isBrowser  Sources/SitboneCore/WindowTitleParser.swift:15  (appName)  TILT
  9 calls  7 worlds  test:7 prod:2
  world  {appName="Google Chrome"}  test:2
  world  {appName=*}                prod:2   SitboneCore.swift:615, WindowTitleParser.swift:21
  world  {appName="Arc"|"Firefox"|"Safari"|"Terminal"|"VS Code"}  test
  members browsers  appName  10
    hit=["Arc","Firefox","Google Chrome","Safari"]
    miss=["Brave Browser","Chromium","Microsoft Edge","Opera","Orion","Vivaldi"]
  tilt   prod-open           appName  tests=[…6 literals including VS Code…]  prod=*
  tilt   unwitnessed-member  appName in browsers  miss=[Brave, Chromium, Edge, Opera, Orion, Vivaldi]
```

kizu `run_split_command` (was buried under test_support):

```
run_split_command  src/attach.rs:97  (cmd, context)  TILT
  world  {cmd=*, context="Ghostty AppleScript split"}  prod
  world  {cmd=*, context="kitty @ launch"|"tmux split-window"|"zellij run"}  prod
  world  {cmd=*, context="sh failing split"|"sh ok"}  test
  tilt   prod-only-const  context  prod=[Ghostty, kitty, tmux, zellij]  tests=[sh failing, sh ok]
```

tenaoshi now speaks:

```
PromptStore.validate  …  TILT
  world  {source="contracts/prompt.md", text=*}  prod   Runtime.swift:49
  world  {source=*, text=*}                      test:8
  tilt   prod-only-const  source  prod=["contracts/prompt.md"]  tests=[]
```

Subjects renamed correctly: `SiteObserver.record`, `CumulativeRecord.accumulate`. `artifactRef` 187 → 3. Interpolation garbage: 0 hits.

## Dogfood targets

- `fixtures/ugly` — Python, JS, Rust, Swift; unicode path; colon filename; spaces; comments; nested git
- sitbone, kizu, voidtrace, tenaoshi, skills, stratal (read-only)

## Surprises

- sitbone's `extractSiteName` is a public function with six careful tests and **no production call sites**. The live path is `SiteResolver`. Coverage would still be green.
- Production `SiteObserver.record` passes `duration=1` (one-second ticks). Tests pass 5, 10, 20, 30, 50, 60, 100, 200, 300 — never 1. The tests inhabit a different clock.
- voidtrace tests pin dozens of `artifactRef` ids that production never constructs as literals; once test defs are not subjects, that explosion vanishes and the remaining tilts are on real kernel/SDK functions.

## Failures (still open)

- Same-named methods across types still share test-file calls when the call has no type prefix (`encodedRequestBody` on three LLM clients). Same-file affinity fixes production; tests in a generated oracle file still fan out.
- JS/TS options-bag worlds remain coarse when values are identifiers (`{ scenario, catalog, ruleset }` vs `{ scenario: "x" }`).
- skills is two Python scripts; stratal is empty. No signal.
- Dynamic production (`prod=*`) inhabits every `==` arm, so `host=="localhost"` counts as prod-inhabited even when production never passes that literal. The collection envelope is the sharper report for that case.

## Suggested mutations

- `seep` — ldd for effects: stain FS/ENV/NET/PROC through the call graph, then join with worlds ("the timeout=0 world is the one that does IO").
- Witness a working-tree diff only (`git diff | cleave --diff`) — which new literals/branches are unpinned.
- Resolve `self`/`this` to the enclosing type so overloaded methods stop sharing test calls.
- Go through `go/ast` / `syn` instead of the lexer for one language, compare recall.

## Kill / keep

**Keep.** The inhabitance join is a small verb with a real sitbone finding (six untested production browser names) that coverage, grep, and blame cannot phrase. v0.2 cut voidtrace tilts by 3× by refusing to treat test helpers as the function under test — the primitive got sharper, not wider.
