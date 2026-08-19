# loam

Write the **tests production already inhabits**, **constructed so instance methods actually call**.

`seep` ranked I/O worlds first and followed renames, but `record` came out as `SiteObserver.record(...)` — not a real call, because there is no `self`. `loam` emits `SiteObserver()` (or reuses an existing test fixture of that type) so the owed world is callable.

Default stdout is still the test file. `--check` lists ranked worlds without writing. `--no-follow` is hatch. `--no-rank` is till. `--no-construct` is seep.

Machine visa is a **skip comment**, not the object.

## Install / run

```bash
chmod +x ./loam
./loam --help
./demo.sh
```

Requires Python 3.9+ and `git` for rename-follow.

## Interaction

```
loam [-C PATH] [FN...]           # runnable test file, I/O first, Type() constructed
loam isWebApp                    # old name: follow to HEAD, still emit isBrowser(...)
loam --report record             # listing, shows construct  SiteObserver()  as observer
loam --emit xctest record        # force XCTest
loam --emit pytest record        # force pytest
loam --json / --ndjson / --porcelain
loam --check record              # exit 1 if due; stdout is the ranked listing
loam --no-follow isBrowser       # hatch/sow identity (HEAD name only)
loam --no-rank connect           # hatch/till order (label / call-site)
loam --no-construct record       # seep: Type.method, no receiver
loam --aka isWebApp=isBrowser
loam --aka-map
```

| code | meaning |
| --- | --- |
| 0 | ok, or `--check` with nothing due |
| 1 | `--check` found due fixtures |
| 2 | usage / IO error |

Instance methods emit `let observer = SiteObserver()` then `observer.record(...)`. Static methods stay `Type.method(...)`. Collection members get `XCTAssertTrue` / `assert`. Dynamic slots `XCTSkip` / `pytest.skip`. No `...` in Swift. Rank: `timeout=0` > getenv/visa path > filesystem > network > other.

## Examples

Instance method — seep cannot call this; loam constructs:

```bash
./loam --emit pytest -C fixtures/construct record
# def test_record_duration_1_site_prod_site():
#     clock = Clock()
#     clock.record(site="prod-site", duration=1)

./loam --no-construct --emit pytest -C fixtures/construct record
# Clock.record(site="prod-site", duration=1)    # seep; not a real call
```

Required-arg init reuses a self-contained test construction:

```bash
./loam --emit pytest -C fixtures/construct detect
# box = SensorBox([])
# box.detect(timeout=0)
```

I/O still first (seep gold):

```bash
./loam --emit pytest -C fixtures/rank fetch
# def test_fetch_timeout_0_name_omega():    # io=timeout  FIRST
#     fetch(name="omega", timeout=0)
```

sitbone `record` — production pins `duration=1`; tests never do:

```bash
./loam -C ~/ghq/github.com/annenpolka/sitbone record
# let observer = SiteObserver()
# throw XCTSkip("dynamic slots: site, phase — production pins duration=1")
```
