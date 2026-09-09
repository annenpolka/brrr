# Host 実機 pytest#13754

Not Dreamer-facing. HOLD for consumer (no View).

pytest 9.1.1 --setup-plan rc=0; test run rc=0.
- pytest 8.4.1 --setup-plan rc=0; explicit `test.py` 4 passed
- pytest 9.0.1 --setup-plan rc=0; explicit `test.py` 4 passed
- pytest 9.0.3 --setup-plan rc=0 (same shared module setup)
- pytest 9.1.0 --setup-plan rc=0; explicit `test.py` 4 passed
- pytest 9.1.1 explicit `test.py` 4 passed
Still HOLD, no View.

Leftover `--setup-show test.py`: 4 passed on 8.4.1–9.1.1. Shared module SETUP `one_or_two[1]` / `foo` then TEARDOWN, then `[2]` / `foo` again. Same plan as `--setup-plan`. No 8/9 delta.

Leftover `--collect-only test.py`: **4 collected** on 8.4.1–9.1.1 (`TestFoo::test_foo[1]`, `test_foo[1]`, `[2]`, `[2]`). Collect-only matches run. No View.

Leftover `--setup-plan test.py`: **4 collected** on 8.4.1–9.1.1. Plan lists shared module SETUP `one_or_two[1]` / `foo` then `[2]` / `foo` again. Same as `--setup-show`. No 8/9 delta. No View.
