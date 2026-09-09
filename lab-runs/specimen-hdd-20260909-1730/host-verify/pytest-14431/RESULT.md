# Host 実機 pytest#14431

HOLD. Simple `add()` test, not a cache bug. Not Dreamer-facing.

Default collection (`pytest` with no file args) skips `test.py` on **all** of 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 (`python_files`; collect/run rc=5, `no tests collected`). An earlier `pytest911.out` with 1 passed was explicit `pytest test.py`, not default collect.

Explicit `pytest test.py`:

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 1 passed |
| 9.0.1 | 0 | 1 passed |
| 9.0.3 | 0 | 1 passed |
| 9.1.0 | 0 | 1 passed |
| 9.1.1 | 0 | 1 passed |

Leftover `python_files = test.py` in `pytest.ini` (default collect, no file args): **1 passed** on 8.4.1–9.1.1. Default skip of `test.py` is `python_files`, not a cache bug.

Leftover `--setup-show test.py`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not change the add() pass.

Leftover `--collect-only` default (no file args): rc=5 no tests collected on 8.4.1–9.1.1. Leftover `--collect-only test.py`: **1 collected** all versions. Collect-only matches run. No View/export.

Leftover `--tb=short test.py`: **1 passed** on 8.4.1–9.1.1. Explicit file still collects `test.py`. No View.

Leftover `--setup-plan test.py`: **1 collected** on 8.4.1–9.1.1. Explicit file still collects `test.py` at plan. No View.

Leftover isolated `alt_pyfiles/` (`python_files = test.py`) `--lf`/`--ff`/`--sw`: **1 passed** on 8.4.1–9.1.1. Default skip of `test.py` is `python_files`, not last-failed. No View.

Leftover isolated `alt_pyfiles/` `--nf`: **1 passed** on 8.4.1–9.1.1. No View.
