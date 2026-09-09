# Host 実機 pytest#14702 / #14700

Not Dreamer-facing. HOLD no View. Do not apply the PR. No jaraco.test tree.

Fixture functions with doctests, including `pytest.skip` inside a doctest, on CPython 3.14.

| pytest | `pytest test_fix.py` | `pytest --doctest-modules test_fix.py` |
| --- | --- | --- |
| 8.4.1 | rc=0 1 pass | rc=0 2 passed, 1 skipped |
| 9.0.1 | rc=0 | rc=0 2 passed, 1 skipped |
| 9.0.3 | rc=0 | rc=0 2 passed, 1 skipped |
| 9.1.0 | rc=0 | rc=0 2 passed, 1 skipped |
| 9.1.1 | rc=0 | rc=0 2 passed, 1 skipped |

No `INTERNALERROR` / `line is not None` on this host (3.14, not reporter's 3.12 + jaraco.test).

Leftover `--setup-show --doctest-modules`: **2 passed, 1 skipped** on 8.4.1–9.1.1. SETUP `doctest_namespace` / `sample`. No INTERNALERROR.

Leftover `--tb=short --doctest-modules`: **2 passed, 1 skipped** on 8.4.1–9.1.1. No INTERNALERROR. No View/export.

Leftover `--collect-only --doctest-modules`: **3 collected** on 8.4.1–9.1.1 (execute is 2 pass 1 skip). No INTERNALERROR at collect. No View/export.
