# mutation-30 — hatch

## Primitive

Default stdout is a **runnable test file** (pytest or XCTest) for the argument worlds production inhabits and tests do not. `--check` still exits 1 if any due world exists.

## Why this might not exist

`sow` (mutation-13) made production argument worlds into fixture records. The daily next step was always the same: turn those records into tests. `--emit pytest` was an afterthought and it emitted **Python** for Swift `isBrowser`. A report you paste into a generator is not a test. Coverage still cannot phrase a missing *value*. The missing Unix verb is **write the file you would drop into Tests/**.

Flipped assumption: the report is opt-in (`--report`). The object is the test.

## How to run

```bash
./hatch --help
./demo.sh
./hatch --self-test
./hatch -C fixtures/ugly isBrowser          # XCTest (Swift subject)
./hatch -C fixtures/ugly connect            # pytest (Python/Rust subjects)
./hatch --report -C /path/to/repo isBrowser # old sow listing
./hatch --check -C /path/to/repo isBrowser  # exit 1 if due; stdout still the tests
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1, commit 19a65cc)

Default output flipped: `hatch -C sitbone isBrowser` wrote XCTest, not a fixture listing. `--check` still exited 1. `@testable import SitboneCore` was already inferred from `Sources/SitboneCore/`.

sitbone `isBrowser` v0.1 (excerpt):

```
import XCTest
@testable import SitboneCore

final class WindowTitleParserHatchTests: XCTestCase {
    func testIsBrowserAppNameBraveBrowser() {
        WindowTitleParser.isBrowser("Brave Browser")
    }
    …
}
```

That file is the right *shape* and the wrong *test*. XCTest treats a bare call as a pass even if `isBrowser` returns false. Production `SiteObserver.record(..., duration: 1)` emitted invalid Swift `...` and would not compile.

### After the improvement (v0.2)

Collection-member fixtures (the production true-set) get `XCTAssertTrue` / `assert`. Dynamic slots become `XCTSkip` / `pytest.skip` with the pinned literals in the reason — no `...` in Swift.

sitbone `isBrowser` after, then actually run (read-only overlay, 2026-08-20):

```
./hatch -C sitbone isBrowser
# import XCTest
# @testable import SitboneCore
# final class WindowTitleParserHatchTests: XCTestCase {
#     func testIsBrowserAppNameBraveBrowser() {
#         XCTAssertTrue(WindowTitleParser.isBrowser("Brave Browser"))
#     }
#     … Chromium, Microsoft Edge, Opera, Orion, Vivaldi
```

```
swift test --filter WindowTitleParserHatchTests
Test Case '...testIsBrowserAppNameBraveBrowser' passed
Test Case '...testIsBrowserAppNameChromium' passed
Test Case '...testIsBrowserAppNameMicrosoftEdge' passed
Test Case '...testIsBrowserAppNameOpera' passed
Test Case '...testIsBrowserAppNameOrion' passed
Test Case '...testIsBrowserAppNameVivaldi' passed
Executed 6 tests, with 0 failures
```

`--check -C sitbone isBrowser` still exits 1 (six dues remain in the real tree). `extractSiteName` stays silent (no production callers). `record` is now:

```
func testRecordSitePhaseDuration1() throws {
    throw XCTSkip("dynamic slots: site, phase — production pins duration=1")
}
```

Census (analysis unchanged from sow v0.2; the object on stdout changed):

```
sitbone    files=49  defs=409  calls=3072  prod_fns=133  due_fns=65  due=80  generable=24
kizu       files=70  defs=1022 calls=10330 prod_fns=382  due_fns=241 due=332 generable=111
```

Ugly fixture: `connect` default is pytest (`timeout=0` skipped as dyn host; `db.example.com` is a real call). `isBrowser` default is XCTest with `XCTAssertTrue` for Brave / Edge.

## Dogfood targets

- `fixtures/ugly` — Python, JS, Rust (lifetimes), Swift; unicode path; colon filename; spaces; comments; nested git
- sitbone `isBrowser` / `record` / `extractSiteName` (read-only; overlay `swift test`)
- kizu `run_split_command` (read-only; `--emit pytest` still available)

## Surprises

- sitbone already had the six missing browsers in the production `browsers` set and four witnessed in `WindowTitleParserTests`. The hatched file is exactly those six `XCTAssertTrue` lines. They compiled and passed on the first overlay run — the oracle *was* the membership, not an invented expected value.
- `record(duration: 1)` is the one production clock world tests never inhabit, but it is an instance method with two dynamic slots. A compilable test is a skip that names the pin, not `SiteObserver.record(..., ..., duration: 1)`.
- `extractSiteName` remains the silent public function with careful tests and zero production call sites. Coverage would still be green.

## Failures (still open)

- Same-named methods across types still share unprefixed calls.
- Instance methods have no `self` construction (`record` cannot be a real call without a `SiteObserver()`).
- JS/TS options-bag worlds remain coarse.
- Display wrappers would still emit one test per chrome string if asked without a name filter.
- `--check` on a whole sitbone tree is noisy (many dues); the useful invocation names a function.

## Suggested mutations

- Construct `Type()` / use existing test fixtures when the subject is an instance method.
- Rank / hide display-wrapper functions before emitting a whole-tree file.
- Append into an existing XCTestCase (`WindowTitleParserTests`) instead of a sibling `*HatchTests` class.
- Join with `seep`: emit the timeout=0 world first because it does IO.

## Kill / keep

**Keep.** The flip is real: sow's sitbone finding (six untested browser names) is now six XCTest methods that `swift test` executed with 0 failures, and `--check` still fails the tree until those worlds live in the real Tests/. v0.2 made the file a test instead of a call list. Kill only if a later generation proves the real object is a patch against the existing test file, not a new file on stdout.
