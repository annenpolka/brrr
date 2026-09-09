# Host 実機 pytest#14700

Not Dreamer-facing. HOLD no View. No jaraco.test clone.

Mini: `pytest.ini` `addopts = --doctest-modules -vv`; `pkg/git.py` fixture `ensure_checkout` whose doctest calls `pytest.skip`. Host CPython 3.14.5 (reporter: 3.12 only).

| pytest | `pytest pkg/git.py` |
| --- | --- |
| 8.4.1 | rc=0 1 skipped (`needs git`); no INTERNALERROR |
| 9.0.1 | rc=0 1 skipped |
| 9.0.3 | rc=0 1 skipped |
| 9.1.0 | rc=0 1 skipped |
| 9.1.1 | rc=0 1 skipped |

Does not reproduce `assert line is not None` on this host. Reporter could not reduce outside jaraco.test on 3.12.

Leftover `--setup-show`: **1 skipped** on 8.4.1–9.1.1; SETUP/TEARDOWN `doctest_namespace`. No INTERNALERROR. No View/export.

Leftover `--collect-only --doctest-modules`: **1 collected** on 8.4.1–9.1.1 (skipped at execute). No View/export.
