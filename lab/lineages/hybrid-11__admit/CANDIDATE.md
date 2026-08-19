# hybrid-11 — admit

## Primitive

A **clearance** is a production argument world fused to the visa its literals imply. Default stdout is a runnable test that asserts that world and skips on machine mismatch. OPEN/SPEC worlds assert. BOUND worlds assert *and* skip unless this host holds the visa.

## Why this might not exist

`hatch` writes the test production already inhabits. `visa` writes the skip an oracle demands. Developers who have both still have two reports: a test that will go red on CI the moment a HOME leaks into a call, and a sidecar predicate they must remember to wrap.

Concatenation is `hatch | visa-the-file`. A `macOS` comment or Alice's path in the same source stains every hatched test. File-as-golden visa of `App.swift` is BOUND Darwin; Brave is then skipped even though `"Brave Browser"` implies no machine.

The object changed. The visa is taken from the world's argument literals only. Skip and assert share that witness set. Changing the host literal changes both.

Discarded as concatenation: wrapping hatch stdout with `visa --emit pytest`; visading the production file and applying one skip to every due world.

## How to run

```bash
chmod +x ./admit
./admit --self-test
./demo.sh
./admit -C fixtures/ugly load_profile
./admit -C ~/ghq/github.com/annenpolka/sitbone isBrowser
./admit --bound --report -C fixtures/ugly
./admit --check --bound -C ~/ghq/github.com/annenpolka/sitbone
```

Python 3.10+, stdlib. Exit 0 on success. `--check` exits 1 if any due world exists. `--check --bound` exits 1 only for machine-tied debt.

## Empirical transcript

### v0.1 (`1eefd79`) — clearance is the object; sitbone is all OPEN

`./admit --self-test` ok. `./demo.sh` → **passed=73 failed=0**.

Alice's home (this host is not Alice):

```
./admit -C fixtures/ugly load_profile
# fate=skipif  visa BOUND  HOME=/Users/alice platform=Darwin
# assert load_profile(home="/Users/alice")
# runtime: SKIP visa MISS HOME want=/Users/alice have=/Users/annenpolka
# hatch-style assert would FAIL: /Users/alice is not a directory
```

This host's HOME MATCH: `probe("/Users/annenpolka")` skipif + assert, **PASS**.

Same Swift file, two worlds:

```
isBrowser("Brave Browser")   OPEN  XCTAssertTrue   no skip
loadHome("/Users/alice/…")   BOUND XCTSkipUnless + XCTAssertTrue
file-as-golden visa         BOUND  (concat would skip Brave)
```

Textbook `/home/user` and `John Doe` → SPEC, assert, no skip. GitHub title `annenpolka/sitbone` → OPEN, not USER.

sitbone (read-only, 2026-08-20):

```
isBrowser     6 OPEN asserts (Brave, Chromium, Edge, Opera, Orion, Vivaldi)
record        dyn XCTSkip (duration=1) — not a visa miss
extractSiteName  silent (no production callers)
--summary     prod_fns=133 due=80 assert=10 skipif=0 skip=70 bound=0 open=80
--check --bound  exit 0
swift test --filter WindowTitleParserAdmitTests  6 tests, 0 failures
```

kizu `--bound` is also empty. Neither tree's production callers leaked a HOME.

### v0.2 — recover the production span (sitbone forced this)

v0.1 emitted hatch's 45-char cut. sitbone `runAppleScript` became `tell application "Safari"\n...`. The GitHub title fixture became `Pull Reque...`. That is not the production world.

After: recover the call at the site span (multiline strings, balanced parens). Drop a world that only repeats a collection member.

```
./admit -C sitbone runAppleScript
# NSWorkspaceWindowMonitor.runAppleScript("""
#     tell application "Safari"
#         if not (exists front document) then return ""
#         return URL of front document
#     end tell
#     """)

./admit -C fixtures/ugly extract_title
# extract_title("GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome")
# not Pull Reque...
```

`isBrowser("Brave Browser")` in `boot()` is no longer a second test. `./demo.sh` → **passed=79 failed=0**. Overlay still 6/6.

## Dogfood targets

- `fixtures/ugly` — Alice home, textbook quote, GitHub title, macOS comment beside Brave, rust lifetimes
- this host's live `$HOME` (MATCH) vs `/Users/alice` (MISS)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` isBrowser / record / extractSiteName / runAppleScript / `--bound`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` `--bound`

## Surprises

- sitbone needed no skip: production never recorded a machine. The joint is still visible — `--check --bound` is the new green, while `--check` stays 1 because six browser members are still due.
- visa of `App.swift` *as source* demotes textbook `alice` to SPEC. The concat lie is treating the file as a golden (`production.world.snap`), which is how you would wrap hatch output as an oracle.
- sitbone's due `runAppleScript` world was the Safari AppleScript, not a path. Recovery was forced by length, not by a visa.

## Failures

- `runAppleScript` is a private instance method. The recovered script is the real oracle; the test still cannot construct `self`.
- `--check` on a whole sitbone tree is noisy (70 dyn skips). `--bound` is the useful grain.
- JS/TS options-bag worlds stay coarse (hatch's).

## Suggested mutations

- Construct `Type()` / use existing fixtures when the subject is an instance method.
- `--held`-style: when did a production world newly acquire a visa?
- Join with alibi: splice admitted tests onto old production (LOCKED-and-BOUND vs LOCKED-and-OPEN).

## Kill / keep

**Keep.** The object is not hatch-then-visa. sitbone isBrowser compiled and passed with no skip; Alice's `load_profile` skipped here and would have failed as a hatch assert. `--check --bound` on sitbone/kizu is the honest "production leaked no machine" signal neither parent speaks. Kill only if a later generation proves `hatch` plus a hand-written `skipif` on the file recovers per-world polarity — it does not, because Brave and Alice share a file and not a visa.
