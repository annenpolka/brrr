# mutation-95 — seat

## Primitive

Untested production argument worlds as methods **appended into the existing test type** (`SiteObserverTests`, `PresenceArbiterTests`), ranked I/O first, with `Type()` only as fallback when no such class exists.

## Why this might not exist

`sow` made production worlds into fixture records. `hatch` made the object a test file. `till` followed renames. `seep` ranked timeout=0 / fs / visa first. `loam` constructed `SiteObserver()` so instance methods actually call. All five still emit a **sibling** `*LoamTests` class. Coverage, `swift test --filter SiteObserverLoamTests`, and XCTest overlay all accept a file that is not the fixture of the type. The class that already knows how to build `SiteObserver` is `SiteObserverTests`.

The missing Unix verb is **owe the world in the existing test type**, not another coverage number and not a machine visa (that object is visa/oath/stain; seat only *comments* a visa path).

Flipped assumption: loam emits `final class SiteObserverLoamTests`. seat emits the owed method inside `SiteObserverTests`. `--no-seat` is loam. `--no-construct` is seep. `--no-rank` is till. `--no-follow` is hatch. `--apply` writes the file. `--diff` is a patch against it.

## How to run

```bash
./seat --help
./demo.sh
./seat --self-test
./seat --emit xctest -C fixtures/seat record
./seat --no-seat --emit xctest -C fixtures/seat record
./seat -C fixtures/seat detect
./seat --diff --emit xctest -C fixtures/seat record
./seat --apply -C /tmp/overlay record
./seat --emit pytest -C fixtures/ugly connect
./seat --check -C fixtures/rank
./fixtures/rename/build.sh /tmp/seat-rename
./seat --no-follow -C /tmp/seat-rename/leftover isBrowser
./seat             -C /tmp/seat-rename/leftover isBrowser
./seat -C /path/to/sitbone record
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1)

Self-test + seat fixture proved the flip. loam / `--no-seat` on `record` emits `SiteObserverSeatTests`. seat emits `SiteObserverTests` with `testRecordFive` kept and the duration=1 world appended:

```
./seat --emit xctest -C fixtures/seat record
# final class SiteObserverTests: XCTestCase {
#     func testRecordFive() { … }
#     func testRecordSiteProdDuration1() {
#         let observer = SiteObserver()
#         observer.record(site: "prod", duration: 1)
#     }
# }

./seat --no-seat --emit xctest -C fixtures/seat record
# final class SiteObserverSeatTests: XCTestCase { … }

./seat -C fixtures/seat detect
# struct PresenceArbiterTests { … testDetectTimeout0 … timeout: 0 }
```

sitbone `record` seats into `Tests/SitboneCoreTests/SiteObserverTests.swift` (`seat  SiteObserverTests  …  xctest`). sitbone `isBrowser` seats Brave/Chromium/Edge/Opera/Orion/Vivaldi into `WindowTitleParserTests` (existing `testChromeTitle` stays). sitbone `logEntry` seats into `struct PresenceArbiterTests` with `@Test(.disabled(…))` — not a sibling XCTestCase.

`--apply` on an overlay writes those files; no `*SeatTests.swift` is created. Overlay `swift test --filter SiteObserverTests` runs existing cases plus the seated skip. Overlay `swift test --filter WindowTitleParserTests` runs existing cases plus Brave.

Rename gold held: leftover Brave still emits under HEAD name `isBrowser`, now inside `WindowTitleParserTests` / `test_web.py`. kizu `install_claude_code` silent under `--no-follow`, four due worlds with follow, `io=fs` on `project_root=*`. Visa remains a skip *comment* only.

v0.1 hole: `detect` (NotchGeometry) scored `SystemSleepTests` because that file also contains `detect(` — a function-name false friend, not `{Type}Tests`.

### After the improvement (v0.2)

A host is a seat only when it **is the test type of the production type**. `{Type}Tests` / `Test{Type}` / `test_{snake}` match. A file that merely contains `detect(` does not.

```
./seat --report -C sitbone detect
# NotchGeometry.detect  …  sown
#   seat  (none)  fallback sibling
# (v0.1: seat  SystemSleepTests  …  swift-testing)
```

Self-test: `NotchGeometry.detect` next to `PresenceArbiterTests` (which calls `detect(`) stays unseated; `--no-seat` sibling is the fallback. sitbone `record` / `isBrowser` / `logEntry` still sit in the exact `{Type}Tests`. Overlay still **13 tests, 0 failures** on `WindowTitleParserTests` and **13 tests, 1 skip, 0 failures** on `SiteObserverTests`.

Census unchanged (ranking/construct/follow are not the axis):

```
sitbone    files=49  defs=452  calls=3072  prod_fns=133  due_fns=65  due=80  generable=24 aka_fns=4 io_due=9
kizu       files=70  defs=1022 calls=10555 prod_fns=382  due_fns=242 due=335 generable=111 aka_fns=4 io_due=171
tenaoshi   files=25  defs=197  calls=1599  prod_fns=107  due_fns=64  due=94  generable=36 aka_fns=0 io_due=20
```

## Dogfood targets

- `fixtures/seat` — SiteObserverTests XCTestCase; PresenceArbiterTests Swift Testing struct; pytest test_clock.py
- `fixtures/construct` — Clock.record instance; Clock.ping static; SensorBox([]) required init; Swift SiteObserverTests
- `fixtures/ugly` — Python, JS, Rust (lifetimes), Swift WindowTitleParserTests; unicode path; colon filename; spaces; comments; nested git
- `fixtures/rank` — timeout=0 sorts last alphabetically, first under seat; `~/.ssh/id_rsa` vs `alpha`; duration=1 is not timeout
- `fixtures/rename` — leftover old-name callers + historical-only literals (till gold)
- sitbone `isBrowser` / `record` / `logEntry` / `extractSiteName` / `stopSession` (read-only; overlay `swift test --filter` existing classes)
- kizu `run_split_command` / `install_claude_code` (read-only)
- tenaoshi `PromptStore.validate` (`source="contracts/prompt.md"` is fs)

## Surprises

- sitbone never renamed `isBrowser`. The six Brave/Chromium/Edge/Opera/Orion/Vivaldi members stay static `WindowTitleParser.isBrowser(...)` — seating is a no-op on construction and a real flip on class identity.
- `SiteObserverTests` is already how every SiteObserver case starts. Reusing that class (not inventing `SiteObserverLoamTests`) is the primitive on a tree that already knew where the fixture lived.
- PresenceArbiter's tests are Swift Testing (`struct PresenceArbiterTests`), not XCTest. The existing type is still the seat; a sibling XCTestCase would have been a second wrong object.
- `SiteObserverPersistenceTests` exists and constructs `SiteObserver()`. Exact `{Type}Tests` must beat the longer name or record sits in the persistence suite.
- kizu `install_claude_code` is still the real-repo rename fixture. Seating does not apply (free function, pytest host if one exists). Ranking and follow are unchanged.

## Failures

- Same-named methods across types still share unprefixed calls (`detect` is NotchGeometry, not PresenceArbiter). v0.2 no longer *seats* that into SystemSleepTests; it still cannot tell PresenceArbiter.detect from NotchGeometry.detect without a type-qualified query.
- `SessionEngine()` is an honest guess, not a compiling construction — there is no self-contained test fixture of that type. The skip comment says so. Seating still appends that guess into `test_engine.py`.
- JS/TS class methods are still poorly parsed (no `function` keyword), so JS instance worlds are mostly free functions.
- Whole-tree `--check` is noisy; the useful invocation names a function (or an old name).
- One hop only. A helper two calls deep from `open` stays unstained.
- Dyn instance worlds skip after constructing; they do not fill `site`/`phase` from production.
- `--apply` twice is idempotent on method names (uniquify) but will re-add a MARK comment if the first apply already seated.

## Suggested mutations

- Resolve `self`/`this` so overloaded methods stop sharing calls (`PresenceArbiter.detect` vs `NotchGeometry.detect`).
- Walk `git log -L` / tree-sitter for hops that are not on adjacent def lines.
- Stain through more than one hop; hide display-wrapper functions before a whole-tree file.
- Join with visa only as a skip *comment*, never as the object.
- Reuse `setUp` instance bindings so seated methods do not re-declare `let observer = SiteObserver()`.

## Kill / keep

**Keep.** The flip is real: `--no-seat` on sitbone `record` is a sibling class; seat writes into `SiteObserverTests` and the overlay compiles (existing cases + 1 skip, 0 failures). sitbone `isBrowser` sits in `WindowTitleParserTests`, not `WindowTitleParserSeatTests`. `PresenceArbiterTests` (Swift Testing) is reused. Kill only if a later generation proves the real object is a merge of the owed world into an existing *test method* (not a new method in the existing class).
