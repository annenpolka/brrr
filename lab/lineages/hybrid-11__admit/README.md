# admit

Write the **tests production already inhabits**, already **visad**.

`hatch` emits a runnable test for each production argument world the suite never passes. `visa` emits the skip/apply predicate an oracle implies. Concatenation visas the production *file* (or the generated file) and wraps every test.

`admit` is one object: a **clearance**. The visa is inferred from the world's argument literals — not from a neighboring `macOS` comment, not from a GitHub title in a different test. OPEN/SPEC worlds assert. BOUND worlds assert the production world **and** skip on machine mismatch.

## Install / run

Python 3.10+, stdlib only. v0.2.

```bash
chmod +x ./admit
./admit --help
./demo.sh
./admit --self-test
```

## Three examples

### 1. Portable production world — assert, no skip

sitbone's untested browser names are not a machine:

```bash
./admit -C ~/ghq/github.com/annenpolka/sitbone isBrowser
# import XCTest
# @testable import SitboneCore
# final class WindowTitleParserAdmitTests: XCTestCase {
#     func testIsBrowserAppNameBraveBrowser() {
#         // visa OPEN  fate=assert
#         XCTAssertTrue(WindowTitleParser.isBrowser("Brave Browser"))
#     }
```

`--check --bound` on sitbone exits 0: production leaked no HOME.

### 2. Machine-tied production world — assert and skip on mismatch

```bash
./admit -C fixtures/ugly load_profile
# def test_load_profile_home_Users_alice():
#     _m = _admit_misses({'HOME': '/Users/alice', 'platform': 'Darwin', ...})
#     if _m:
#         pytest.skip('visa MISS ' + '; '.join(_m))
#     assert load_profile(home="/Users/alice")
```

On this host the test **skips**. A hatch-style bare `assert load_profile("/Users/alice")` **fails** (`/Users/alice` is not a directory). On Alice's Mac it asserts.

### 3. Same file, two worlds, two visas

`fixtures/ugly/src/App.swift` has a `macOS` comment, `isBrowser("Brave Browser")`, and `loadHome("/Users/alice/Library/sitbone")`. File-level visa is BOUND Darwin. Brave is still OPEN. Alice's home is skipif.

```bash
./admit --emit xctest -C fixtures/ugly isBrowser loadHome
./admit --bound --report -C fixtures/ugly   # only the Alice debt
```

Textbook `/home/user` and `John Doe` are SPEC (assert, no skip). A sitbone-shaped GitHub title is OPEN (not `USER=you`).

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due (or `--check --bound` with no machine-tied debt) |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |
