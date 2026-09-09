# Host 実機 pytest#13699

Not Dreamer-facing. HOLD for HDD consumer (no View/export). Isolated venv, not pytest's own suite.

CPython 3.14.5 + asynctest 0.13.0:
- `import asynctest` rc=1 `AttributeError: module 'asyncio' has no attribute 'coroutine'`
- `pytest.importorskip("asynctest")` rc=1 same AttributeError on 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 (does not skip; importorskip only catches ImportError)

Matches the reporter's asynctest traceback. Dead third-party on 3.14, not a pytest 8/9 delta.

Leftover without the isolated asynctest tree: `importorskip` **1 skipped** (ImportError). Leftover `PYTHONPATH=/tmp/hdd-13699-asynctest-only`: still rc=1 `AttributeError: module 'asyncio' has no attribute 'coroutine'` on 8.4.1–9.1.1. importorskip only skips ImportError.

Leftover `--setup-show` with that PYTHONPATH: still 1 failed AttributeError coroutine on 8.4.1–9.1.1. `--setup-show` does not skip it. No View staged.

Leftover `--tb=short` with `PYTHONPATH=/tmp/hdd-13699-asynctest-only`: still AttributeError `asyncio.coroutine` on 8.4.1–9.1.1 (1 failed). Short traceback does not skip the import. No View/export.

Leftover `--assert=plain` with `PYTHONPATH=/tmp/hdd-13699-asynctest-only`: still AttributeError `asyncio.coroutine` on 8.4.1–9.1.1. Plain assert does not skip the import. No View/export.

Leftover `--tb=line` with PYTHONPATH asynctest: still AttributeError `asyncio.coroutine` on 8.4.1–9.1.1. Line traceback does not skip the import. No View/export.
