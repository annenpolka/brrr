# Host 実機 pytest#14255

Not Dreamer-facing. HOLD (docs). No View. Do not apply the PR.

Quoted vs integer `log_cli_level` in pyproject.

| layout | 8.4.1 | 9.0.1 | 9.0.3 | 9.1.0 | 9.1.1 |
| --- | --- | --- | --- | --- | --- |
| `[tool.pytest] log_cli_level = "INFO"` | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 |
| `[tool.pytest.ini_options] log_cli_level = "INFO"` | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 |
| `[tool.pytest] log_cli_level = 10` | rc=0 (native table unread) | rc=3 TypeError | rc=3 | rc=3 | rc=3 TypeError |

Quoted string works on pytest 9 native table. Integer does not. Matches the docs claim.

Leftover `--collect-only`: quoted native and `ini_options` **1 collected** on 8.4.1–9.1.1. Integer native: 8.4.1 **1 collected** (table unread); pytest 9 rc=3 TypeError `log_cli_level` int 10 at config. Collect-only still hits the native-table TypeError.

Leftover `--setup-show` quoted: **1 passed** on 8.4.1–9.1.1. Leftover `--setup-show` int native: 8.4.1 **1 passed** (unread); pytest 9 rc=3 INTERNALERROR TypeError at configure. Same split as collect-only. No View/export.

Leftover `--tb=short` isolated `quoted/`: 1 passed all. Leftover isolated `int_native/ --tb=short`: 8.4.1 1 passed (native table unread); pytest 9 INTERNALERROR TypeError `log_cli_level` int. `--tb=short` does not skip configure TypeError. Parent-tree `--tb=short` hits leftover dummy-name collisions. No View.

Leftover `--setup-plan` quoted: **1 collected** all versions. Leftover `--setup-plan` int_native: 8.4.1 **1 collected**; pytest 9 rc=3 TypeError at configure. Same as collect-only / `--tb=short`. No View.

Leftover quoted `--lf`/`--ff`/`--nf`/`--sw`: **1 passed** on 8.4.1–9.1.1. Leftover int_native `--lf`/`--ff`/`--nf`/`--sw`: 8.4.1 **1 passed**; pytest 9 TypeError at configure (not last-failed). No View.

Leftover int_native `--maxfail=1`: 8.4.1 **1 passed**; pytest 9 rc=3 TypeError at configure (not last-failed). `--maxfail=1` does not skip configure INTERNALERROR. No View.
