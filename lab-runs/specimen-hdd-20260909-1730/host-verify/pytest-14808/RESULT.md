# Host 実機 pytest#14808

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

`addini(..., type="string")` plus a TOML array, then `config.getini("mystr")`.
- `[tool.pytest.ini_options] mystr = ["not","a","string"]`: 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=1, getini returns a list (`assert isinstance(val, str)` fails; no TypeError)
- `[tool.pytest] mystr = ["not","a","string"]`: 8.4.1 rc=0 (table unread, default string); 9.0.1/9.0.3/9.1.0/9.1.1 rc=1 TypeError expects string, got list
- `pytest.ini` scalar: 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=0

Matches the reported toml-vs-ini_options split. No View staged.

Leftover `--collect-only` per layout (`ini_options/`, `tool_pytest/`, `pytest_ini/`): **1 collected** on 8.4.1–9.1.1. Collect-only does not execute `getini`, so the TypeError/list assert is not visible at collect. Parent-dir collect hits leftover `test_dummy.py` name collisions.

Leftover `--setup-show` per layout (executes `getini`):
- `ini_options/`: **1 failed** `isinstance(['not','a','string'], str)` on 8.4.1–9.1.1 (list, no TypeError)
- `tool_pytest/`: 8.4.1 **1 passed** (native unread); pytest 9 TypeError expects string, got list
- `pytest_ini/`: **1 passed** all (INI scalar)

`--setup-show` surfaces the getini split that collect-only hid. No View.

Leftover `--tb=short` `ini_options/`: still 1 failed `isinstance(['not', 'a', 'string'], str)` on 8.4.1–9.1.1. Short traceback still shows the getini list. No View.

Leftover `--tb=short` `tool_pytest/`: 8.4.1 **1 passed** (native table unread). Pytest 9 **1 failed** TypeError getini list. `--tb=short` still shows the TypeError. No View.

Leftover `--tb=short` `pytest_ini/`: **1 passed** on 8.4.1–9.1.1 (INI scalar `mystr`). `--tb=short` does not surface a getini TypeError on this layout. No View.

Leftover `--setup-plan` `pytest_ini/`: **1 collected** on 8.4.1–9.1.1. No tests ran. INI scalar does not error at plan. No View.

Leftover `ini_options/` `--lf`/`--ff`/`--nf`: still **1 failed** `isinstance(['not','a','string'], str)` on 8.4.1–9.1.1. Leftover `--sw`: 1 failed interrupted (stuck on the list assert). Leftover `tool_pytest/` `--lf`/`--ff`/`--sw`/`--nf`: 8.4.1 **1 passed** (native unread); pytest 9 TypeError getini list still (execute last-failed). No View.

Leftover `pytest_ini/` `--nf`: **1 passed** on 8.4.1–9.1.1. Leftover `tool_pytest/` `--maxfail=1`: 8.4.1 **1 passed**; pytest 9 still 1 failed TypeError (does not skip configure/execute TypeError). No View.
