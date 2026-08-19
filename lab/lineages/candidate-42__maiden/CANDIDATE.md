# candidate-42 — maiden

## Primitive

The set of tests whose recorded outcome history (junit, cargo/libtest, swift,
CI logs, jsonl ledger) contains **zero failures** — not the set that `rg PASS`
on the newest run.

## Why this might not exist

TDD requires red first. Coverage says a line ran. alibi asks whether current
tests would fail on old production. cinch 1-minimizes production hunks the
suite vetoes. None of them ask: **has this test identity ever been observed
red on this host / in this CI?** A test written after the fix, a generated
test, a skip-only stub, and a 2019 failure that has been green for years all
look the same in the latest log.

The skeptic pipeline is `rg PASS latest.xml`. That keeps repaired scars,
drops skips, and cannot name UNKNOWN. maiden folds history.

Discarded: alibi, cinch, winnow, leftover-name, inverse-printf, third ambit,
fourth cinch, existing-tool+LLM.

## How to run

```bash
chmod +x ./maiden ./demo.sh
./maiden --selftest
./demo.sh
./maiden --no-ledger --header fixtures/junit/run-2019-fail.xml fixtures/junit/run-2024-green.xml
./maiden --no-ledger --latest --counts fixtures/junit/run-2019-fail.xml fixtures/junit/run-2024-green.xml
./maiden --no-ledger --skeptic fixtures/junit/run-2019-fail.xml fixtures/junit/run-2024-green.xml
./maiden --no-ledger --roster --counts /path/to/swift-test-list.txt
```

Python 3.10+, stdlib. Exit 0 ok, 1 `--check` fired, 2 usage.

## Empirical transcript

### v0.1 — fold + skeptic + skip-not-maiden (`1638f8d`)

`--selftest` 26/26. Fixture junit 2019-fail + 2024-green:

| id | history | `--latest` | skeptic |
| --- | --- | --- | --- |
| pkg.T::alpha | SCARRED (fail 2019, pass 2024) | MAIDEN | yes |
| pkg.T::beta | MAIDEN (2 pass) | MAIDEN | no |
| pkg.T::gamma | SKIPPED | SKIPPED | no |
| pkg.T::delta | MAIDEN (born 2024) | MAIDEN | no |

`--latest` reports SCARRED 0 MAIDEN 3. Full history SCARRED 1 MAIDEN 2. never-red
is empirically not `rg PASS`.

GHA-prefixed cargo log: `kizu::scar::undo` fail then pass → SCARRED / skeptic;
`kizu::hook::parse` only pass → MAIDEN.

### Dogfood (before identity fix)

No junit, no xcresult, no `.build/logs/unit.log` on sitbone. `gh run view --log`
is HTTP 410 for kizu/sitbone failures (CI was April–May 2026). Honest ledger is
empty.

`swift test list --skip-build` on sitbone: **213** specifiers. v0.1 roster parser
accepted only one `/` → **177 UNKNOWN**, dropped **36** nested Swift Testing
ids (`PresenceArbiterTests/EMASmoothing/firstReadingNoSmoothing()`). MAIDEN 0.

One live `swift test --filter UILogicTests/formatTimeZero`: log is
`✔ Test "formatTime: ゼロ" passed`. Roster id is
`SitboneUITests.UILogicTests/formatTimeZero`. Join: specifier stays UNKNOWN,
display name is ORPHAN MAIDEN. A green run did **not** maiden the roster
entry. XCTest `-[Class testName]` *does* join `Class/testName`.

kizu `cargo test -- --list`: **489** `: test` rows, all UNKNOWN. One exact
`app::tests::compute_operation_diff_empty_when_identical` becomes MAIDEN and
joins the list identity. Rust is not the Swift split.

### v0.2 — identity is the runner specifier (from that dogfood)

v0.1 roster regex allowed one ASCII `/`. sitbone list 213 → classified 177.
36 nested Swift Testing ids vanished, including Japanese
`SystemSleepTests/ウェイク処理/cameraRestartsAfterWake()`. A green
`formatTime: ゼロ` log maidened an ORPHAN display name and left the roster
specifier UNKNOWN — never-red looked like a second `rg PASS` lie.

v0.2: nested `/` segments (Unicode), and `-C Tests/` maps `@Test("display")`
plus nested `struct` path onto `Module.Type[/Nested]/func`. `--no-alias-swift`
is the v0.1 split.

After:

| tree | v0.1 | v0.2 |
| --- | --- | --- |
| sitbone `swift test list` | UNKNOWN **177** / 213 | UNKNOWN **213** / 213 |
| sitbone one green `formatTime: ゼロ` | ORPHAN display, specifier UNKNOWN | **MAIDEN** `SitboneUITests.UILogicTests/formatTimeZero`, ORPHAN 0, UNKNOWN 212 |
| kizu `cargo --list` | UNKNOWN 489 | UNKNOWN 489 (cargo id already = list) |

`--selftest` 28/28. `./demo.sh` 27 passed, 0 failed.

never-red is still not `rg PASS`: 213 sitbone tests that would all PASS today
are UNKNOWN until an outcome is recorded, and a 2019 junit fail stays SCARRED
after a 2024 green file.

## Dogfood targets

- fixtures/junit, cargo, gha, swift
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (swift test list + one filter)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (cargo --list + one exact)

## Surprises

1. Empty history is not maiden — sitbone/kizu CI being green does not produce a
   never-red set without a ledger.
2. Swift Testing **display name ≠ specifier**, including Japanese `@Test("…")`.
3. Nested Swift Testing suites use extra `/`, and some nested *types* are
   Japanese identifiers (`struct ウェイク処理`). ASCII `Type/name` drops them.

## Failures

- GitHub Actions job logs expired (410); cannot scar kizu from real CI.
- xcresulttool not exercised (no `.xcresult` on disk).
- Source `--census` ids are function names, not runner specifiers.
- Ambiguous duplicate `@Test("same")` strings across suites are not aliased.

## Suggested mutations

- Persist `gh run view --log` into the ledger before 410.
- `--min-runs N` as policy, not the primitive.
- Parametrized cargo `foo/bar` vs Swift `Suite/name`.
- xcresult as a first-class ingest (not xcresulttool JSON walk).

## Kill / keep

**Keep.** The object survived: latest-green ∩ historical-fail is a named set
`--skeptic`; skip-only is not maiden; no records is UNKNOWN. Kill only if a
later tool shows never-red is just `alibi` on HEAD — it is not; alibi splices
production, maiden folds outcome history.
