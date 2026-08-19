# hatch

Write the **tests production already inhabits**.

`sow` printed fixture records a generator might consume. `hatch` kills the report. Default stdout is a **runnable test file** — pytest if the dues are Python/JS/Rust, XCTest if they are Swift. Tests are still a subtract filter: only production worlds the existing tests never pass.

`--check` still exits 1 when any due world exists. The file is what you owe; the exit code is whether you owe it.

## Install / run

```bash
chmod +x ./hatch
./hatch --help
./demo.sh
```

Requires Python 3.9+.

## Interaction

```
hatch [-C PATH] [FN...]          # runnable test file (default)
hatch --report isBrowser         # human listing (opt-in)
hatch --emit xctest isBrowser    # force XCTest
hatch --emit pytest connect      # force pytest
hatch --json / --ndjson / --porcelain
hatch --check isBrowser          # exit 1 if any due world; stdout still the tests
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

## Examples

Swift collection members the tests never pass — default is XCTest, not a report:

```bash
./hatch -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# import XCTest
# @testable import SitboneCore
# final class WindowTitleParserHatchTests: XCTestCase {
#     func testIsBrowserAppNameBraveBrowser() {
#         XCTAssertTrue(WindowTitleParser.isBrowser("Brave Browser"))
#     }
#     …
```

Python production `timeout=0` the tests never pass — default is pytest:

```bash
./hatch -C fixtures/ugly connect
# def test_connect_timeout_0_host():
#     pytest.skip('dynamic slots: host — production pins timeout=0')
```

CI still fails while dues exist:

```bash
./hatch --check -C . isBrowser > /tmp/DueIsBrowserTests.swift
echo $?   # 1
```
