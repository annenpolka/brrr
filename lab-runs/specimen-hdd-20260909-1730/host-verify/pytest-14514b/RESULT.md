# Host 実機 pytest#14514 python_files workaround

Not Dreamer-facing. HOLD feature. No View. Do not apply PR #14750.

`[tool.pytest.ini_options] python_files = ["*.test.py", "test_*.py"]` then collect `pkg/foo.test.py`.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 2 | `ModuleNotFoundError: No module named 'pkg.foo'` |
| 9.0.1 | 2 | same |
| 9.0.3 | 2 | same |
| 9.1.0 | 2 | same |
| 9.1.1 | 2 | same |

`--import-mode=importlib` with the same `python_files` + path: 8.4.1/9.0.1/9.1.1 collect rc=0 (`pkg/foo.test.py::test_foo`) and 8.4.1/9.1.1 run rc=0 (1 passed). Default import mode still ImportError.

Leftover `--collect-only` default: rc=2 `ModuleNotFoundError` on 8.4.1–9.1.1. Leftover `--collect-only --import-mode=importlib`: **1 collected** all versions. Same as run.

Leftover `--setup-show --import-mode=importlib`: **1 passed** (`pkg/foo.test.py::test_foo`) on 8.4.1–9.1.1. No View/export.
