# tide

Test oracles as a time series.

An oracle is the *claimed expected value*: the literal in `assert_eq!` /
`expect().toBe` / `#expect` / `assertEqual`, or a scalar leaf in an
`*expected*.json` / contract testcase. tide walks first-parent git history
and classifies how each claim moved — not whether the test passed.

## Install / run

Python 3.9+ and `git`. No other dependencies.

```bash
./tide --help
./demo.sh
./tide --selftest
```

Copy `tide` onto your `PATH` if you want. Exit 0 on a successful walk,
1 with `--check` when BLESS or FLIPFLOP is present, 2 on tool error.

## Examples

**1. Which expected values in this repo have changed their mind?**

```bash
./tide -C /path/to/repo
```

```
RATCHET,BLESS    json   contracts/testcases/CTR-008.json
  CTR-008  $.max_length_ratio
  0.95 → 0.99
  a41089c1  2026-04-07  BORN      0.95
  4878b752  2026-07-20  BLESS     0.99
```

`BLESS` means the oracle moved in a commit that did not touch production
files — the test was updated to match the code, or relaxed to go green.

**2. Version literals ratchet. Sequence arrays flip-flop.**

```bash
./tide -C /path/to/voidtrace --kind inline
```

```
RATCHET   packages/kernel/src/rejected-rule-trace.test.ts
  outcome.result.fingerprint.engineVersion
  "0.19.0" → "0.20.0" → "0.21.0" → "0.22.0"

FLIPFLOP  packages/kernel/src/evaluate.test.ts
  outcome.trace.decisions.map((decision) => decision.sequence)
  [0,1,2,3,4,5] → [0,1,2,3,4] → [0,1,2,3,4,5]
```

**3. One oracle, machine-readable.**

```bash
./tide series 'hits[0].message' -C /path/to/kizu --json
./tide -C /path/to/repo --json --check
```

`--json-mode naive` flattens whole JSON testcases (including `input`).
Default `roots` keeps only `expectation` / `expected_*` subtrees.
Default porcelain hides STABLE claims; `--all` shows them.

Classes: STABLE, DRIFT, RATCHET, FLIPFLOP, VANISH, plus a BLESS tag.
