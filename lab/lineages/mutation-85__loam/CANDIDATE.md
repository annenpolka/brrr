# mutation-85 — loam

## Primitive

Untested production argument worlds as a **runnable test file**, ranked I/O first, with **instance methods constructed** (`Type()` or a self-contained test fixture of that type) so `record` is a real call, not `SiteObserver.record(...)`.

## Why this might not exist

`sow` made production worlds into fixture records. `hatch` made the object a test file. `till` followed renames. `seep` ranked timeout=0 / fs / visa first. All four still emit instance methods as `Type.method(...)` — which is not a call. Coverage, `grep fn(`, and XCTest overlay all accept the file and then fail to compile, or compile a skip that never built a receiver.

The missing Unix verb is **owe a constructed call**, not another coverage number and not a machine visa (that object is visa/oath/stain; loam only *comments* a visa path).

Flipped assumption: seep emits `SiteObserver.record(...)`. loam emits `let observer = SiteObserver()` then `observer.record(...)`. `--no-construct` is seep. `--no-rank` is till. `--no-follow` is hatch.

## How to run

```bash
./loam --help
./demo.sh
./loam --self-test
./loam --emit pytest -C fixtures/construct record
./loam --no-construct --emit pytest -C fixtures/construct record
./loam --emit pytest -C fixtures/construct detect
./loam --emit pytest -C fixtures/ugly connect          # pytest; timeout=0 first
./loam --check -C fixtures/rank
./fixtures/rename/build.sh /tmp/loam-rename
./loam --no-follow -C /tmp/loam-rename/leftover isBrowser
./loam             -C /tmp/loam-rename/leftover isBrowser
./loam -C /path/to/sitbone record
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1)

Self-test + construct fixture proved the flip. seep / `--no-construct` on `record` emits `Clock.record` / `SiteObserver.record` (not callable). loam emits a receiver:

```
./loam --emit pytest -C fixtures/construct record
# clock = Clock()
# clock.record(site="prod-site", duration=1)

./loam --no-construct --emit pytest -C fixtures/construct record
# Clock.record(site="prod-site", duration=1)

./loam --emit pytest -C fixtures/construct detect
# box = SensorBox([])
# box.detect(timeout=0)

./loam -C sitbone record
# let observer = SiteObserver()
# throw XCTSkip("dynamic slots: site, phase — production pins duration=1")
```

Static methods stay Type.method: `WindowTitleParser.isBrowser("Brave Browser")`, `Clock.ping(...)`. duration=1 is still not timeout=0. Rename-follow leftover Brave still emits. Overlay `swift test --filter WindowTitleParserLoamTests`: **Executed 6 tests, with 0 failures**. Overlay `SiteObserverLoamTests`: constructed, 1 skipped, 0 failures.

v0.1 hole on sitbone: `SessionEngine(deps: deps)` was treated as a test fixture because the value identifier matched the label. That does not compile outside the test's local `deps`. Swift `init(` was not parsed (it is not `func init`), so required inits looked like zero-arg.

### After the improvement (v0.2)

Fixes: a label does not launder a local (`deps: deps` is not self-contained); parse Swift `init(` so required vs zero-arg is known; dyn skip tests `_ = observer` so the receiver is used; visa remains a skip *comment* only.

```
./loam -C sitbone record
# let observer = SiteObserver()
# _ = observer
# // observer.record(_, _, duration: 1)
# throw XCTSkip("dynamic slots: site, phase — production pins duration=1")

# PresenceArbiter still reuses the empty-literal test construction:
#   construct  PresenceArbiter(sensors: [])  via test-fixture

# SessionEngine no longer copies the local:
#   construct  SessionEngine()  via guess
#   // no self-contained test fixture; SessionEngine() may need args
```

`--report record` shows `construct  SiteObserver()  as observer  via test-fixture`. `--no-construct` still restores seep. CJK `挨拶("世界")` is not fs. kizu `install_claude_code` silent under `--no-follow`, four due worlds with follow, `io=fs` on `project_root=*`.

Census (analysis close to seep v0.2; Swift `init` defs are new, ranking/construct is the axis):

```
sitbone    files=49  defs=452  calls=3072  prod_fns=133  due_fns=65  due=80  generable=24 aka_fns=4 io_due=9
kizu       files=70  defs=1022 calls=10555 prod_fns=382  due_fns=242 due=335 generable=111 aka_fns=4 io_due=171
tenaoshi   files=25  defs=197  calls=1599  prod_fns=107  due_fns=64  due=94  generable=36 aka_fns=0 io_due=20
```

sitbone defs 409→452 and tenaoshi 170→197 because `init(` is now a def (used to choose Type() vs guess, not as a subject — `init` stays in SKIP_SUBJECT).

## Dogfood targets

- `fixtures/construct` — Clock.record instance; Clock.ping static; SensorBox([]) required init; Swift SiteObserver
- `fixtures/ugly` — Python, JS, Rust (lifetimes), Swift; unicode path; colon filename; spaces; comments; nested git
- `fixtures/rank` — timeout=0 sorts last alphabetically, first under loam; `~/.ssh/id_rsa` vs `alpha`; duration=1 is not timeout
- `fixtures/rename` — leftover old-name callers + historical-only literals (till gold)
- sitbone `isBrowser` / `record` / `extractSiteName` / `stopSession` / `PresenceArbiter` / `SessionEngine` (read-only; overlay `swift test`)
- kizu `run_split_command` / `install_claude_code` (read-only)
- tenaoshi `PromptStore.validate` (`source="contracts/prompt.md"` is fs)

## Surprises

- sitbone never renamed `isBrowser`. The six Brave/Chromium/Edge/Opera/Orion/Vivaldi members stay static `WindowTitleParser.isBrowser(...)` — construction is a no-op on that subject and must stay one.
- `SiteObserver()` is already how every SiteObserverTests case starts. Reusing that test-fixture expression (not inventing a new one) is the primitive on a tree that already knew how to build the type.
- `PresenceArbiter(sensors: [])` is self-contained (empty collection literal). `SessionEngine(deps: deps)` is not — `deps` is a local that happens to share the label name. v0.1's first self-contained checker treated labels as value identifiers.
- Swift constructors are `init(`, not `func init`. Until that was a def, every type looked zero-arg.
- kizu `install_claude_code` is still the real-repo rename fixture. Construction does not apply (free function). Ranking and follow are unchanged.
- Binding name is the last CamelCase word: SiteObserver → `observer`, PresenceArbiter → `arbiter`, SensorBox → `box`. That matched the sitbone tests without copying their locals.

## Failures

- Same-named methods across types still share unprefixed calls (`detect` is NotchGeometry, not PresenceArbiter).
- `SessionEngine()` is an honest guess, not a compiling construction — there is no self-contained test fixture of that type. The skip comment says so.
- JS/TS class methods are still poorly parsed (no `function` keyword), so JS instance worlds are mostly free functions.
- Whole-tree `--check` is noisy; the useful invocation names a function (or an old name).
- One hop only. A helper two calls deep from `open` stays unstained.
- Dyn instance worlds skip after constructing; they do not fill `site`/`phase` from production.

## Suggested mutations

- Append into an existing XCTestCase (`SiteObserverTests`) instead of a sibling `*LoamTests` class — that *is* the test fixture of the type.
- Resolve `self`/`this` so overloaded methods stop sharing calls (`PresenceArbiter.detect` vs `NotchGeometry.detect`).
- Walk `git log -L` / tree-sitter for hops that are not on adjacent def lines.
- Stain through more than one hop; hide display-wrapper functions before a whole-tree file.
- Join with visa only as a skip *comment*, never as the object.

## Kill / keep

**Keep.** The flip is real: `--no-construct` on sitbone `record` cannot call; loam constructs `SiteObserver()` and the overlay compiles (1 skip, 0 failures). sitbone `isBrowser` still 6/6 static. `PresenceArbiter(sensors: [])` is reused; `SessionEngine(deps: deps)` is not. Kill only if a later generation proves the real object is a patch against the existing test file (reuse `SiteObserverTests` as the fixture), not a new file on stdout with a constructor.
