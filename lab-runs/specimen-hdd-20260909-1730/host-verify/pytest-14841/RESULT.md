# Host 実機 pytest#14841

Not Dreamer-facing. HOLD no View.

Public snippet from the issue body (`conftest.py` + `test_demo.py`, `pytest_plugins = 'pytester'`). Host CPython 3.14.5 macOS. Default `skip_by_default` collects the four `test_run_mp_test` cases.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | 3 passed, 1 failed `test_run_mp_test[deferred-import-fail]` |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |

Failure: nested pytester run of a failing `multiprocessing.Pool` workload with deferred import leaves `resource_tracker` KeyError on stderr (`cache[rtype].remove(name)`). Pre-import cases pass. Matches the reporter. Repair PR #14850 stays 正解 off Dreamer.

Leftover `--tb=short`: pytest 9 still 1 failed / 3 passed (`resource_tracker`). 8.4.1 this run 4 passed (flaky stderr). Traceback style does not change the KeyError.

Leftover `--collect-only test_demo.py`: **10 collected** on 8.4.1–9.1.1. `resource_tracker` is execute, not collect. No View/export.

Leftover `--setup-show`: still 1 fail `resource_tracker` KeyError on 8.4.1–9.1.1 (flaky 8.4.1 `--tb=short` 4-pass does not mint PASS). `--setup-show` does not skip the deferred import. No View.

Leftover `--nf`: 8.4.1 1 failed 3 passed; 9.1.0/9.1.1 this run 4 passed (flaky stderr, HOLD). Leftover `--sw`: 8.4.1 first 1 failed 3 passed, second 1 failed 9 deselected. Leftover `--maxfail=1`: 1 failed 3 passed all versions. No View.
