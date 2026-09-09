# Host 実機 pytest#9298

Not Dreamer-facing. HOLD no View. Not Windows.

`PYTHONPYCACHEPREFIX=<prefix> pytest src/test_foo.py` on macOS CPython 3.14.5.

| pytest | rc | rewritten pyc under prefix |
| --- | --- | --- |
| 8.4.1 | 0 | `.../src/test_foo.cpython-314-pytest-8.4.1.pyc` present |
| 9.0.1 | 0 | `.../src/test_foo.cpython-314-pytest-9.0.1.pyc` present |
| 9.0.3 | 0 | present |
| 9.1.0 | 0 | present |
| 9.1.1 | 0 | `.../src/test_foo.cpython-314-pytest-9.1.1.pyc` present |

The Windows CI missing-pyc assertion does not reproduce here.

Leftover `--setup-show src/test_foo.py`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not drop the rewritten pyc under PYTHONPYCACHEPREFIX.

Leftover `--collect-only src/test_foo.py`: **1 collected** on 8.4.1–9.1.1. No View/export.

Leftover `--tb=short src/test_foo.py`: **1 passed** on 8.4.1–9.1.1. Short traceback does not change the pygments rewrite. No View.
