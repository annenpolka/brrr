# till

Write the **tests production already inhabits**, following **renames**.

`hatch` made the object a runnable test file. It still treated the **HEAD token** as the subject. If `isBrowser` was `isWebApp` last week, leftover (or last week's) `isWebApp("Brave Browser")` callers are invisible. `till` flips that: identity is the git rename chain. Default stdout is still the test file. `--report` is the sow listing. `--check` exits 1 if any due world exists.

## Install / run

```bash
chmod +x ./till
./till --help
./demo.sh
```

Requires Python 3.9+ and `git` for rename-follow.

## Interaction

```
till [-C PATH] [FN...]          # runnable test file (default)
till isWebApp                   # old name: follow to HEAD, still emit isBrowser(...)
till --report isBrowser         # human listing, shows aka / follow hops
till --emit xctest isBrowser    # force XCTest
till --emit pytest connect      # force pytest
till --json / --ndjson / --porcelain
till --check isBrowser          # exit 1 if any due world; stdout still the tests
till --no-follow isBrowser      # hatch/sow identity (HEAD name only)
till --aka isWebApp=isBrowser   # manual alias when git hops are missing
till --aka-map                  # identity table (even when sown)
till --since 2026-01-01
till --range HEAD~20..HEAD
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

Collection-member fixtures get `XCTAssertTrue` / `assert`. Dynamic slots `XCTSkip` / `pytest.skip`. No `...` in Swift. Tests are emitted under the **HEAD** name.

## Examples

A rename sow/hatch miss — leftover production still calls the old name:

```bash
./fixtures/rename/build.sh /tmp/till-rename
./till --no-follow --emit pytest -C /tmp/till-rename/leftover isBrowser
# (no Brave — HEAD identity)

./till --emit pytest -C /tmp/till-rename/leftover isBrowser
# def test_isBrowser_name_Brave_Browser():
#     isBrowser(name="Brave Browser")

./till --emit pytest -C /tmp/till-rename/leftover isWebApp
# same file: query by the dead name, emit the living one
```

sitbone `isBrowser` — six production browsers the tests never pass, as XCTest:

```bash
./till -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# import XCTest
# @testable import SitboneCore
# final class WindowTitleParserHatchTests: XCTestCase {
#     func testIsBrowserAppNameBraveBrowser() {
#         XCTAssertTrue(WindowTitleParser.isBrowser("Brave Browser"))
#     }
#     …
```

CI still fails while dues exist:

```bash
./till --check -C . isBrowser > /tmp/DueIsBrowserTests.swift
echo $?   # 1
```
