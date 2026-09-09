# Host 実機 pytest#14514

HOLD feature. `pkg/foo.test.py` collect:
8.4.1/9.0.1/9.1.1 rc=2 `ModuleNotFoundError: No module named 'foo.test'`.
`--import-mode=importlib` on the same path: 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 collect/run rc=0 (1 passed).

Leftover `pythonpath = pkg` plus `python_files = *.test.py`: default collect still `ModuleNotFoundError: No module named 'foo.test'; 'foo' is not a package` on 8.4.1–9.1.1. `--import-mode=importlib` still 1 passed. pythonpath does not fix default import of dotted `*.test.py`.

Leftover `--setup-show --import-mode=importlib` (no file args, parent tree): rc=5 no tests ran on 8.4.1–9.1.1 (default python_files skip `foo.test.py`; leftover `alt_pp/` also present). Explicit file still needed. Not Dreamer-facing. No View.
