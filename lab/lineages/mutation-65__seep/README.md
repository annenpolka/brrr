# seep

Write the **tests production already inhabits**, **I/O worlds first**.

`hatch` made the object a runnable test file. `till` followed renames so `isWebApp` last week still defines worlds. Both emit in call-site or label order — `db.example.com` before `timeout=0`. `seep` flips that: the timeout=0 / filesystem / network / getenv world is the one that flakes and the one no unit test wrote, so it is the first method in the file.

Default stdout is still the test file. `--check` lists ranked worlds without writing. `--no-follow` is hatch. `--no-rank` is till's order.

Machine visa is a **rank signal**, not the object. That object is visa/oath/stain.

## Install / run

```bash
chmod +x ./seep
./seep --help
./demo.sh
```

Requires Python 3.9+ and `git` for rename-follow.

## Interaction

```
seep [-C PATH] [FN...]           # runnable test file, I/O worlds first
seep isWebApp                    # old name: follow to HEAD, still emit isBrowser(...)
seep --report isBrowser          # human listing, shows aka / io= tags
seep --emit xctest isBrowser     # force XCTest
seep --emit pytest connect       # force pytest
seep --json / --ndjson / --porcelain
seep --check isBrowser           # exit 1 if due; stdout is the ranked listing
seep --check --emit pytest …     # exit 1; stdout is still the test file
seep --no-follow isBrowser       # hatch/sow identity (HEAD name only)
seep --no-rank connect           # hatch/till order (label / call-site)
seep --aka isWebApp=isBrowser    # manual alias when git hops are missing
seep --aka-map
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

Collection-member fixtures get `XCTAssertTrue` / `assert`. Dynamic slots `XCTSkip` / `pytest.skip`. No `...` in Swift. Tests are emitted under the **HEAD** name. Rank: `timeout=0` > getenv/visa path > filesystem > network > other.

## Examples

The timeout=0 world sorts last alphabetically and first under seep:

```bash
./seep --emit pytest -C fixtures/rank fetch
# def test_fetch_timeout_0_name_omega():    # io=timeout  FIRST
#     fetch(name="omega", timeout=0)
# def test_fetch_name_alpha_timeout_30():
#     fetch(name="alpha", timeout=30)

./seep --no-rank --emit pytest -C fixtures/rank fetch
# alpha first — hatch/till order
```

A rename sow/hatch miss — leftover production still calls the old name:

```bash
./fixtures/rename/build.sh /tmp/seep-rename
./seep --no-follow --emit pytest -C /tmp/seep-rename/leftover isBrowser
# (no Brave — HEAD identity)

./seep --emit pytest -C /tmp/seep-rename/leftover isBrowser
# def test_isBrowser_name_Brave_Browser():
#     assert isBrowser(name="Brave Browser")
```

sitbone `isBrowser` — six production browsers the tests never pass, as XCTest:

```bash
./seep -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# import XCTest
# @testable import SitboneCore
# final class WindowTitleParserSeepTests: XCTestCase {
#     func testIsBrowserAppNameBraveBrowser() {
#         XCTAssertTrue(WindowTitleParser.isBrowser("Brave Browser"))
#     }
#     …
```

CI lists the owed I/O worlds without dumping a module:

```bash
./seep --check -C . connect
# timeout  connect  {host=*, timeout=0}  …
echo $?   # 1
```
