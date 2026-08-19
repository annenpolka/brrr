# seat

Write the **tests production already inhabits** into the **existing test type**, not a sibling class.

`loam` constructed `SiteObserver()` so `record` was a real call, then emitted a sibling `SiteObserverLoamTests`. That class is not the fixture of the type. `SiteObserverTests` already is. `seat` appends the owed world there. `Type()` is only the fallback when no such class exists.

Default stdout is the seated existing file. `--apply` writes it. `--diff` is a unified diff against it. `--check` lists ranked worlds without writing. `--no-seat` is loam. `--no-construct` is seep. `--no-rank` is till. `--no-follow` is hatch.

Machine visa is a **skip comment**, not the object.

## Install / run

```bash
chmod +x ./seat
./seat --help
./demo.sh
```

Requires Python 3.9+ and `git` for rename-follow.

## Interaction

```
seat [-C PATH] [FN...]           # existing test type with owed worlds seated
seat isWebApp                    # old name: follow to HEAD, still emit isBrowser(...)
seat --apply record              # write into SiteObserverTests.swift
seat --diff record               # unified diff against that file
seat --report record             # listing, shows seat  SiteObserverTests  …  xctest
seat --emit xctest record        # force XCTest methods (host dialect still wins)
seat --check record              # exit 1 if due; stdout is the ranked listing
seat --no-seat record            # loam: sibling *SeatTests class
seat --no-construct record       # seep: Type.method, no receiver
seat --no-rank connect           # hatch/till order
seat --no-follow isBrowser       # hatch/sow identity
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

When `{Type}Tests` exists, new methods go in that class. Static methods stay `Type.method(...)`. Collection members get `XCTAssertTrue` / `#expect` / `assert`. Dynamic slots `XCTSkip` / `@Test(.disabled)` / `pytest.skip`. No `...` in Swift. Rank: `timeout=0` > getenv/visa path > filesystem > network > other.

## Examples

Append into the XCTestCase that already tests the type (loam wrote a sibling):

```bash
./seat --emit xctest -C fixtures/seat record
# final class SiteObserverTests: XCTestCase {
#     func testRecordFive() { … }          # existing
#     func testRecordSiteProdDuration1() {  # seated
#         let observer = SiteObserver()
#         observer.record(site: "prod", duration: 1)
#     }
# }

./seat --no-seat --emit xctest -C fixtures/seat record
# final class SiteObserverSeatTests: XCTestCase { … }   # loam
```

Swift Testing struct is also a seat — not a new XCTestCase:

```bash
./seat -C fixtures/seat detect
# struct PresenceArbiterTests {
#     @Test func defaultTimeout() { … }    # existing
#     @Test func testDetectTimeout0() {    # seated
#         let arbiter = PresenceArbiter(sensors: [])
#         arbiter.detect(timeout: 0)
#     }
# }
```

sitbone `record` — production pins `duration=1`; tests never do. The object is `SiteObserverTests`, not `SiteObserverSeatTests`:

```bash
./seat -C ~/ghq/github.com/annenpolka/sitbone record
# final class SiteObserverTests: XCTestCase {
#     func testRecordFlowVisit() { … }     # existing
#     func testRecordSitePhaseDuration1() throws {
#         let observer = SiteObserver()
#         throw XCTSkip("dynamic slots: site, phase — production pins duration=1")
#     }
# }
```
