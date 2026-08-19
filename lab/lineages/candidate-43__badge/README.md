# badge

Never-red tests keyed by **(suite, class, method)** — not the string spelling
maiden folds, and not `rg PASS` on the newest junit.

A currently green test is not maiden. SKIP-only is not maiden. No records is
**UNKNOWN**, not maiden. `<flakyFailure>`, `<rerunFailure>`, and
`status="failed"` are **red**. One fail in 2019 is **SCARRED** even if every
run since has passed.

```
MAIDEN    ≥1 pass, 0 fail
SCARRED   ≥1 fail (error, flakyFailure, rerunFailure, status=failed count)
SKIPPED   only skip/ignored — never executed as pass or fail
UNKNOWN   in the roster, never an outcome
ORPHAN    has outcomes, not in the current roster
```

Not alibi (would these tests go red on old production). Not cinch (which hunks
the suite vetoes). Not maiden's opaque `classname::name` string: the object is
the **badge** `(suite, class, method)`. A method rename
(`compute_diff` → `compute_operation_diff`) and a class move (`pkg.Old::alpha`
→ `pkg.New::alpha`) are one identity. `--no-unify` is the string-id lie.

## Install / run

Python 3.10+, stdlib.

```bash
chmod +x ./badge ./demo.sh
./badge --selftest
./demo.sh
./badge --help
```

Ledger default: `ROOT/.badge/ledger.jsonl`.

```json
{"id":"pkg.T::alpha","status":"fail","t":"2019-06-01T12:00:00Z","suite":"pkg","class":"pkg.T","method":"alpha"}
```

Exit 0 ok, 1 `--check` fired, 2 usage (`--latest --skeptic` is 2: that composition is `rg PASS`).

## Examples

### 1. Latest green is not never-red

```bash
./badge --no-ledger --header \
  fixtures/junit/run-2019-fail.xml \
  fixtures/junit/run-2024-green.xml
```

`pkg.T::alpha` failed in 2019 and passed in 2024 → **SCARRED**. `--latest`
(newest outcome only) reports it **MAIDEN**. `--skeptic` prints that set:
latest PASS ∩ history FAIL. `--latest --skeptic` is refused.

### 2. `<flakyFailure>` is a red

```bash
./badge --no-ledger --header fixtures/junit/flaky-then-green.xml
```

Surefire/Jenkins retry XML records the failed attempt as `<flakyFailure>`, not
`<failure>`. maiden called this MAIDEN. badge scars it. Same for
`<rerunFailure>` and `status="failed"` with no child.

### 3. Rename is one identity; roster without history is UNKNOWN

```bash
./badge --no-ledger --header \
  fixtures/junit/rename-fail.xml \
  fixtures/junit/rename-pass.xml
# SCARRED  pkg.T::compute_operation_diff  n_fail=1 n_pass=1  aka=pkg.T::compute_diff
# --skeptic  SKEPTIC 1   (maiden string-id: SKEPTIC 0)

./badge --no-ledger --roster --counts fixtures/roster/sitbone-list.txt
# SCARRED 0  MAIDEN 0  SKIPPED 0  UNKNOWN 213  ORPHAN 0
```

Co-occurrence in the same src/run keeps the 213 specifiers from collapsing.
SKIP-only (`fixtures/junit/skip-only.xml`) is SKIPPED, and `--check MAIDEN`
exits 0.

```bash
./badge ingest --run ci-2024 fixtures/junit/run-2024-green.xml
./badge --only MAIDEN
./badge why 'pkg.T::alpha'
./badge --skeptic --check SKEPTIC
```
