# Host 実機 pytest#14004 public `testpaths` outside rootdir

Not Dreamer-facing. HOLD no View. Related PRs #14098/#14118 stay 正解 off Dreamer.

Public layout: `sdk/pyproject.toml` `testpaths = ["../tests/sdk"]`; nested autouse `outer_fixture` / `inner_fixture`. Run from `sdk/`.

Counts: 1 inner test + 2 outer tests. `inner_fixture` on outer tests is the leak.

| pytest | `cd sdk && pytest -s` (testpaths) | `cd sdk && pytest -s ../tests/sdk` |
| --- | --- | --- |
| 8.4.1 | rc=0; inner=3 outer=3 (leak) | rc=0; inner=1 outer=3 (no leak) |
| 9.0.1 | leak | no leak |
| 9.0.3 | leak | no leak |
| 9.1.0 | inner=1 outer=3 (no leak) | no leak |
| 9.1.1 | no leak | no leak |

Matches the reporter on 8.4.1–9.0.3. Leak gone from 9.1.0. Earlier `pytest-14004` mini ran from the tests tree and did not reproduce.

Leftover `pythonpath = ["../tests/sdk"]` next to `testpaths` (same `cd sdk && pytest -s`): still leak inner=3/outer=3 on 8.4.1–9.0.3; inner=1/outer=3 from 9.1.0. pythonpath does not change the leak.

Leftover `--setup-show` from `sdk/` (testpaths): 8.4.1–9.0.3 SETUP `inner_fixture` **3** + `outer_fixture` 3 (leak). 9.1.0/9.1.1 SETUP `inner_fixture` **1** + `outer_fixture` 3 (no leak). Same split as `-s` counts. No View.

`--rootdir=.` from `sdk/`: rootdir stays `sdk`; leak still 8.4.1–9.0.3, gone 9.1.0.
`--rootdir=..` from `sdk/`: rootdir is the parent; rc=5 no tests ran (testpaths relative to parent miss). No View/export.

Leftover `--collect-only` from `sdk/` (testpaths): **3 collected** on 8.4.1–9.1.1 (`inner/test_inner`, `test_outer`, `test_outer_2`) — not 4. The inner autouse leak is execute (`--setup-show` 3 vs 1), not collect. No View.

Leftover `--setup-plan` from `sdk/` (testpaths): 8.4.1–9.0.3 lists `inner_fixture` on inner **and** both outer tests (leak at plan). 9.1.0/9.1.1 lists `inner_fixture` on inner only; outer tests `outer_fixture` only. Same split as `--setup-show` execute. No tests ran. No View.

Leftover `--lf` from `sdk/`: **3 passed** then `--lf` **3 passed** (no previously failed tests) on 8.4.1–9.1.1. Inner autouse leak does not fail, so it is not last-failed. No View.

Leftover `--ff`/`--nf`/`--sw` from `sdk/`: **3 passed** on 8.4.1–9.1.1. Leak is execute, not last-failed / failed-first / stepwise. No View.

Leftover `--maxfail=1` from `sdk/`: **3 passed** on 8.4.1–9.1.1. No View.
