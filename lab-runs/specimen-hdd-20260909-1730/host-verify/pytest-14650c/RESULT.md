# Host 実機 pytest#14650 leftover ini tables

Not Dreamer-facing. HOLD no View.

Same `test_strict.py` (`(1, 2)` vs `("1", 2)`). Isolated trees.

| config | 8.4.1 | 9.0.1–9.1.1 |
| --- | --- | --- |
| `pytest.ini` `[pytest] strict_parametrization_ids = true` | rc=0 collect; unknown-option warning; ids `1-2_0` `1-2_1` | rc=2 duplicate IDs ERROR |
| `pyproject.toml` `[tool.pytest.ini_options]` same key | rc=0 collect; unknown-option warning; same auto-suffix | rc=2 duplicate IDs ERROR |

8.4.1 does not know the option (warns, auto-suffixes). pytest 9 honors both `pytest.ini` `[pytest]` and `ini_options`. Isolated no-config is `pytest-14650b`.

Leftover `--collect-only`: `pytest.ini` and `ini_options` both **2 collected** on 8.4.1 (unknown-option warning + auto-suffix); pytest 9 rc=2 duplicate IDs ERROR. Same as run. No View/export.

Leftover `--setup-plan` `ini_pytest/`: 8.4.1 2 items. Pytest 9 (9.0.1–9.1.1) collect ERROR duplicate IDs / `strict_parametrization_ids`. Same as collect-only. No View.

Leftover `--lf` `ini_pytest/test_strict.py`: 8.4.1 seed 2 pass 1 warning; `--lf` no last-failed, 2 pass. Pytest 9 both runs collect ERROR duplicate IDs. Collect-error is not last-failed. No View.

Leftover `--maxfail=1` `ini_pytest/test_strict.py`: 8.4.1 **2 passed** 1 warning both runs. Pytest 9 both runs collect ERROR duplicate IDs. `--maxfail=1` does not skip collect-error. No View.

Leftover `ini_options/` `--lf`/`--ff`/`--nf`/`--sw` `test_strict.py`: same split as `ini_pytest/` (8.4.1 2 pass 1 warning; pytest 9 collect-error duplicate IDs). Collect-error is not last-failed / failed-first / new-first / stepwise. No View.
