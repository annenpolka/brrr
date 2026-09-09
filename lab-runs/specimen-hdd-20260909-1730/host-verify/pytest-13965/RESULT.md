# Host 実機 pytest#13965 N=1

Not Dreamer-facing. HOLD no View. Internals SHAs not passed to Dreamer.

Default collection skips `test.py` on 8.4.1–9.1.1 (rc=5). Explicit `pytest test.py`: 8.4.1 rc=0; 9.0.1 rc=0; 9.0.3 rc=0; 9.1.0 rc=0; 9.1.1 rc=0. N=1 only.

Leftover `-o python_files=test.py` default collect: **1 passed** on 8.4.1–9.1.1 (same as 14431).

Leftover `--collect-only` default: rc=5 no tests collected on 8.4.1–9.1.1. Leftover `--collect-only test.py`: **1 collected** all. Collect-only matches run. No View.

Leftover `--setup-show test.py`: **1 passed** on 8.4.1–9.1.1. Pytest 9 reports `1000 subtests passed`; 8.4.1 does not. `--setup-show` does not change the subtest-times split. No View.

Leftover `--setup-plan -o python_files=test.py test.py`: **1 collected** on 8.4.1–9.1.1. No tests ran. Subtest-times split is execute, not plan. No View.
