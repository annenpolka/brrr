# Host 実機 pytest#14092

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public `[tool.pytest] tmp_path_retention_count = 1` (integer).
- pytest 8.4.1 `[tool.pytest]`: dummy test rc=0 (table unread)
- pytest 8.4.1 `[tool.pytest.ini_options]` int: rc=0
- pytest 9.0.1 `[tool.pytest]`: rc=3 INTERNALERROR `expects a string, got int: 1`
- pytest 9.0.3 `[tool.pytest]`: rc=3 INTERNALERROR TypeError
- pytest 9.1.0 `[tool.pytest]`: rc=3 INTERNALERROR TypeError
- pytest 9.1.1 `[tool.pytest]`: rc=3 same TypeError
- pytest 9.1.1 `[tool.pytest.ini_options]` int: rc=0

No View staged.

Leftover `--collect-only`: pytest 9 still rc=3 TypeError `tmp_path_retention_count` int at config. 8.4.1 collect-only hits leftover dummy-name collision (table unread).

Leftover `--setup-show` isolated `ini_options/`: **1 passed** on 8.4.1–9.1.1. The TypeError is native `[tool.pytest]`, not ini_options. No View.

Leftover parent `--lf`: 8.4.1 rc=2 leftover dummy-name collision. Pytest 9 rc=3 TypeError at configure (not last-failed). Isolated `ini_options/` `--lf`/`--ff`/`--nf`/`--sw`: **1 passed** on 8.4.1–9.1.1. No View.
