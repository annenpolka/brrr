# Host 実機 pytest#14650 without `strict_parametrization_ids`

Not Dreamer-facing. HOLD no View. Isolated tree (no parent `pyproject.toml`).

Same `test_strict.py` (`(1, 2)` vs `("1", 2)`).

| pytest | collect | run |
| --- | --- | --- |
| 8.4.1 | rc=0; ids `1-2_0` `1-2_1` | rc=0 2 passed |
| 9.0.1 | same auto-suffix | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Without the strict ini, pytest 9 does **not** ERROR; it suffixes duplicate IDs. The original `pytest-14650` ERROR is the `[tool.pytest] strict_parametrization_ids = true` table (parent walk from a nested dir also enables it).

Leftover `--collect-only` / `--setup-show`: **2 collected** auto-suffix `1-2_0`/`1-2_1`, **2 passed** on 8.4.1–9.1.1. Same as run. No View/export.

Leftover `--setup-plan test_strict.py` isolated no-strict: **2 collected** on 8.4.1–9.1.1 (auto-suffix IDs; no duplicate ERROR). No tests ran. No View.

Leftover `--lf` after isolated no-strict pass: seed **2 passed**; `--lf` **2 passed** (no previously failed tests) on 8.4.1–9.1.1. Auto-suffix IDs are not last-failed. No View.
