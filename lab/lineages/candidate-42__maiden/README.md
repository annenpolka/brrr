# maiden

Tests whose **recorded history contains zero failures**.

A currently green test is not maiden. `rg PASS` on the newest junit is not maiden.
SKIP-only is not maiden. No records is **UNKNOWN**, not maiden. One fail in 2019 is
**SCARRED** even if every run since has passed.

```
MAIDEN    ≥1 pass, 0 fail
SCARRED   ≥1 fail (error counts as fail)
SKIPPED   only skip/ignored — never executed as pass or fail
UNKNOWN   in the roster, never an outcome
ORPHAN    has outcomes, not in the current roster
```

Not alibi (would these tests go red on old production). Not cinch (which hunks
the suite vetoes). Not winnow (dirty-tree partition). The object is the
**never-red set** under a ledger of junit / cargo / swift / CI logs / jsonl.

## Install / run

Python 3.10+, stdlib. `git` unused. `swift` / `cargo` only to produce a roster.

```bash
chmod +x ./maiden ./demo.sh
./maiden --selftest
./demo.sh
./maiden --help
```

Ledger default: `ROOT/.maiden/ledger.jsonl` (jsonl; one observation per line).

```json
{"id":"pkg.T::alpha","status":"fail","t":"2019-06-01T12:00:00Z","src":"ci.xml","run":"2019"}
```

## Examples

### 1. Latest green is not never-red

```bash
./maiden --no-ledger --header \
  fixtures/junit/run-2019-fail.xml \
  fixtures/junit/run-2024-green.xml
```

`pkg.T::alpha` failed in 2019 and passed in 2024 → **SCARRED**.
`--latest` (newest outcome only) reports it **MAIDEN**. `--skeptic` prints that
set: latest PASS ∩ history FAIL. That is the `rg PASS` lie.

### 2. SKIP-only is not maiden

```bash
./maiden --no-ledger --only SKIPPED fixtures/junit/run-2019-fail.xml
```

`pkg.T::gamma` has only `<skipped/>`. It is not PASS and not MAIDEN.

### 3. Roster without history is UNKNOWN

```bash
cargo test -- --list | ./maiden --no-ledger --roster --counts
swift test list --skip-build | ./maiden --no-ledger --roster --counts
```

sitbone/kizu have no local junit/xcresult; GitHub Actions logs are HTTP 410.
A 213-test roster is 213 UNKNOWN, not 213 maiden.

Swift Testing logs `Test "formatTime: ゼロ"`; `swift test list` emits
`SitboneUITests.UILogicTests/formatTimeZero()`. Nested suites add extra
slashes, including Japanese type names (`SystemSleepTests/ウェイク処理/…`).
`-C` a tree with `Tests/` maps display names onto specifiers. `--no-alias-swift`
keeps the split.

```bash
./maiden ingest --run ci-2024 fixtures/junit/run-2024-green.xml
./maiden --only MAIDEN
./maiden why 'pkg.T::alpha'
./maiden --skeptic --check SKEPTIC
```

`--check MAIDEN` exits 1 if any never-red tests exist (TDD gate: these have
never been observed to fail). Exit 0 ok, 1 check fired, 2 usage.
