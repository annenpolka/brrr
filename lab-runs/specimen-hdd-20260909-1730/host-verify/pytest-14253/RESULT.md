# Host 実機 pytest#14253

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public `pyproject.toml` sets `[tool.pytest] log_cli_level = 0` (integer).
- pytest 8.4.1 `[tool.pytest]`: dummy test rc=0 (8.4.1 does not apply that table)
- pytest 8.4.1 `[tool.pytest.ini_options]` with the same TOML int: rc=0
- pytest 9.0.1 `[tool.pytest]`: rc=3 INTERNALERROR `expects a string, got int: 0`
- pytest 9.0.3 `[tool.pytest]`: rc=3 INTERNALERROR TypeError
- pytest 9.1.0 `[tool.pytest]`: rc=3 INTERNALERROR TypeError
- pytest 9.1.1 `[tool.pytest]`: rc=3 same TypeError
- pytest 9.1.1 `[tool.pytest.ini_options]` with the same TOML int: rc=0

TypeError is the native `[tool.pytest]` table on pytest 9, not ini_options. No View staged.

Leftover `--collect-only`: pytest 9 still rc=3 TypeError `log_cli_level` int at config (collect-only does not skip it). 8.4.1 collect-only of this tree hits leftover dummy-name collision instead of TypeError (table unread).

Leftover `--setup-show` isolated `ini_options/`: **1 passed** on 8.4.1–9.1.1. The TypeError is native `[tool.pytest]`, not ini_options. No View.

Leftover parent `--lf`: 8.4.1 rc=2 leftover dummy-name collision (`ini_options/test_dummy.py` vs parent). Pytest 9 rc=3 TypeError at configure (not last-failed). Isolated `ini_options/` `--lf`/`--ff`/`--nf`/`--sw`: **1 passed** on 8.4.1–9.1.1. No View.
