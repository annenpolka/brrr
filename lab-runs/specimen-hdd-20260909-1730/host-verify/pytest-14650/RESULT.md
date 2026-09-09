# Host 実機 pytest#14650

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public `test_strict.py` with `strict_parametrization_ids = true`.
- pytest 8.4.1: rc=0 2 passed (`strict_parametrization_ids` unknown / `[tool.pytest]` unread)
- pytest 9.0.1: rc=2 collection error duplicate IDs `1-2` for `(1, 2)` vs `("1", 2)`
- pytest 9.0.3: rc=2 same
- pytest 9.1.0: rc=2 same
- pytest 9.1.1: rc=2 same

Leftover: a nested `nostict/` dir still ERROR on pytest 9 because pytest walks up to this tree's `pyproject.toml`. Isolated sibling `pytest-14650b` (no pyproject) auto-suffixes IDs and 2-passes.

Leftover `--collect-only test_strict.py` (`--ignore=nostict --ignore=ini_options`): 8.4.1 **2 collected** auto-suffix `1-2_0`/`1-2_1`. Pytest 9 rc=2 duplicate IDs (same as run). Default directory collect of this tree also hits leftover subdirs (`test_strict` import collision).

Leftover `--tb=short test_strict.py` (same ignores): 8.4.1 2 passed; pytest 9 rc=2 duplicate IDs (from 9.0.1). `--tb=short` does not change collect errors. No View staged.

Leftover `--setup-plan test_strict.py`: 8.4.1 2 items auto-suffix. Pytest 9 (9.0.1–9.1.1) collect ERROR `Duplicate parametrization IDs` / `strict_parametrization_ids`. Same as collect-only. No View.

Leftover `--lf` explicit `test_strict.py`: 8.4.1 2 pass. Pytest 9 collect duplicate IDs; `--lf` still collect ERROR (not last-failed). Bare `--lf` without a file arg walks leftover nested `nostict/`/`ini_options/` copies. No View.

Leftover `--ff` explicit `test_strict.py`: 8.4.1 2 pass. Pytest 9 collect duplicate IDs; `--ff` still collect ERROR (not last-failed). Bare `--ff` without a file arg walks leftover nested copies. No View.
