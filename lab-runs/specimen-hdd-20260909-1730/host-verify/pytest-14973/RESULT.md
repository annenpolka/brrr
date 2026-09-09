# Host 実機 pytest#14973

Not Dreamer-facing. HOLD no View. Do not apply the PR.

`unittest.addModuleCleanup` writes `_cleanup_flag.txt` after the module.

| runner | rc | flag after |
| --- | --- | --- |
| `python -m unittest test_mod` (3.14) | 0 | `cleaned` |
| pytest 8.4.1 | 0 | missing |
| pytest 9.0.1 | 0 | missing |
| pytest 9.0.3 | 0 | missing |
| pytest 9.1.0 | 0 | missing |
| pytest 9.1.1 | 0 | missing |

Cleanup runs under stdlib unittest and does not run under pytest on any version tried.

`unittest.enterModuleContext`: stdlib unittest flag=`exited`. pytest 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 flag=`entered` (enter ran, exit did not).

Leftover `--setup-show`: 2 passed on 8.4.1–9.1.1 (unittest `setUpClass` fixtures). Closing `enterModuleContext` generator still ignored (`AttributeError: 'NoneType' object has no attribute 'write_text'`). `--setup-show` does not run module cleanup.

Leftover `--tb=short`: **2 passed** on 8.4.1–9.1.1; stderr still `Exception ignored` / `NoneType.write_text`. `--tb=short` does not run module cleanup. No View/export.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. Missing module cleanup is execute, not collect. No View/export.
