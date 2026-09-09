# Host 実機 pytest#9703 / #14571 same-named tests under `-c config/`

Not Dreamer-facing. HOLD no View. Do not apply PRs #14571/#14579/#14837.

Public shape: `config/pytest.ini`; `tests/test_file1.py` and `tests/test_file2.py` both define `test_same`.

| pytest | `-c config/pytest.ini` + explicit files | same + `--rootdir=.` |
| --- | --- | --- |
| 8.4.1 | rc=0; both displayed `config::test_same` | rc=0; unique `tests/test_file*.py::test_same` |
| 9.0.1 | same collapse | unique |
| 9.0.3 | same | unique |
| 9.1.0 | same | unique |
| 9.1.1 | same | unique |

9.1.1 lastfailed: fail file1 then `--lf` reruns **both** (1 failed, 1 passed, no deselected). Display/cache key `config::test_same` matches both files. `--rootdir=.` keeps unique nodeids.

`--rootdir=. --lf` after the same fail: **1 failed** only (file2 not rerun). Unique nodeids restore lastfailed selection.

Leftover `--setup-show -c config/pytest.ini` explicit files: **2 passed** on 8.4.1–9.1.1; both displayed `::test_same`. `--setup-show` does not uniquify collapsed nodeids. No View/export.

Leftover `--collect-only -c config/pytest.ini`: **2 collected** both displayed `::test_same` on 8.4.1–9.1.1. Collapsed nodeids are collect-time. No View/export.
