# Host 実機 pytest#14737

Not Dreamer-facing. HOLD no View.

Package-level `pytestmark = pytest.mark.skip` in `skippedpkg/__init__.py`.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | `test_should_be_skipped` FAILED `assert False` (skip did not apply) |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |
| 8.4.1 `pytestmark` in `conftest.py` | 1 | skip does not apply |
| 9.1.1 `pytestmark` in `conftest.py` | 1 | skip does not apply |
| 9.1.1 `pytestmark` in the test module | 0 | 1 skipped |

Package/`conftest` pytestmark does not propagate; module-level does.

Leftover `--collect-only skippedpkg`: **1 collected** as `<Function test_should_be_skipped>` on 8.4.1–9.1.1 (not a skipped collect item). Package pytestmark skip does not apply at collection either.

Leftover `conftest.py` pytestmark on 9.0.1/9.1.0: still **1 failed** (`assert False`; skip does not apply). Leftover module-level pytestmark on 8.4.1/9.0.1/9.1.0: **1 skipped**. Same as 9.1.1 already recorded.

Leftover `--setup-show skippedpkg`: rc=1, `assert False` on 8.4.1–9.1.1. Skip still does not apply at execute.

Leftover `--setup-plan skippedpkg`: rc=0, **no tests ran**, lists `<Function test_should_be_skipped>` on 8.4.1–9.1.1 (not a skipped collect item). Package pytestmark skip does not apply at plan either.

Leftover `--tb=short skippedpkg`: rc=1, `assert False` on 8.4.1–9.1.1. Traceback style does not apply the skip.

Leftover `--lf` after package pytestmark fail: 8.4.1–9.1.1 still **1 failed** `assert False`. Last-failed rerun does not apply the skip either. No View/export.

Leftover `--ff` / `--sw` `skippedpkg`: still **1 failed** `assert False` on 8.4.1–9.1.1 (`--sw` interrupted both runs). Failed-first and stepwise do not apply the package pytestmark skip. No View/export.
