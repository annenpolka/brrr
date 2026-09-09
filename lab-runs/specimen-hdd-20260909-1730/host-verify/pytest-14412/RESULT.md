# Host 実機 pytest#14412

Not Dreamer-facing. HOLD no View. Sleep shortened.

`console_output_style = times` in `[tool.pytest]` (not `ini_options`).

| pytest | rc | times |
| --- | --- | --- |
| 8.4.1 | 0 | no per-subtest us (8.4.1 did not apply `[tool.pytest]`) |
| 9.0.1 | 0 | first subtest ~170us; later `0.000us` |
| 9.0.3 | 0 | first ~128us; later `0.000us` |
| 9.1.0 | 0 | first ~105us; later `0.000us` |
| 9.1.1 | 0 | first ~165us; later `0.000us` |

Leftover `[tool.pytest.ini_options]` times: 8.4.1 **reads** the option (nodeid + `157.1ms` for the whole test; **no** per-subtest us). Pytest 9 still first ~109us later `0.000us`. Leftover `pytest.ini` `[pytest]` times: same (8.4.1 whole-test ms, no subtest lines; pytest 9 later `0.000us`). 8.4.1 original had no times because native `[tool.pytest]` was unread, not because times was off. Later-subtest `0.000us` is pytest 9 regardless of ini table.

Leftover `--setup-show` of the parent tree hits leftover layout name collisions. Per-table times results already recorded. No View/export.

Leftover `--collect-only` of isolated `alt_ini/` and `alt_iniopt/`: **1 UnitTestCase collected** on 8.4.1–9.1.1. The times split (8.4.1 whole-test ms / pytest 9 later `0.000us`) is execute, not collect. No View/export.

Leftover `--durations=0` on isolated `alt_ini/`: 8.4.1 **1 passed** (2 durations hidden). Pytest 9 **1 passed, 3 subtests passed** (5 durations hidden). `--durations=0` does not print per-subtest `us` the way `console_output_style=times` does. No View/export.

Leftover isolated `alt_ini/`/`alt_iniopt/` `--lf`/`--ff`: **1 passed** on 8.4.1–9.1.1 (pytest 9 reports 3 subtests). No last-failed. Times split is execute, not last-failed. No View.

Leftover isolated `alt_ini/` `--maxfail=1`: **1 passed** on 8.4.1–9.1.1 (pytest 9 3 subtests). No View.
