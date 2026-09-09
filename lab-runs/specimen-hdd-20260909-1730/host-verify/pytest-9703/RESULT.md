# Host 実機 pytest#9703 `-c config/pytest.ini` fixture merge

Not Dreamer-facing. HOLD no View. Do not apply PR #14837.

Public layout: `config/pytest.ini`, `tests/test_file1.py` (autouse print), `tests/test_file2.py`.

| pytest | `-c config/pytest.ini` + explicit files | `-c` no args | no `-c` |
| --- | --- | --- | --- |
| 8.4.1 | rc=0; `rootdir: .../config`; nodeids `config::test_in_file*`; autouse runs on **both** tests | rc=0; `config/tests/test_file*.py`; autouse only file1 | rc=0; `tests/test_file*.py`; autouse only file1 |
| 9.0.1 | same merge | same | same |
| 9.0.3 | same merge | same | same |
| 9.1.0 | rc=0; still `config::` nodeids; autouse **only file1** | autouse only file1 | autouse only file1 |
| 9.1.1 | same as 9.1.0 | same | same |

Collapsed `config::` nodeids remain 8.4.1–9.1.1 with explicit paths. Autouse leak is gone from 9.1.0.

`--rootdir=.` on 8.4.1/9.1.1: unique `tests/test_file*.py` nodeids; autouse only file1. Same control as #13246.

Leftover `--setup-show -c config/pytest.ini tests/test_file1.py tests/test_file2.py`: 8.4.1–9.0.3 SETUP `some_fixture` **twice** (autouse leak). 9.1.0/9.1.1 SETUP **once**. Same leak split as run.

Leftover `--collect-only -c config/pytest.ini` those files: **2 collected** collapsed `::test_in_file1` / `::test_in_file2` on 8.4.1–9.1.1. Autouse leak is execute. No View/export.

Leftover `--setup-plan -c config/pytest.ini` explicit files: 8.4.1–9.0.3 SETUP `some_fixture` for **both** tests. 9.1.0/9.1.1 SETUP `some_fixture` for `test_in_file1` only; `test_in_file2` listed without the autouse. Autouse leak is visible at plan (same split as `--setup-show` execute). No tests ran. No View/export.

Leftover `--lf` after `-c config/pytest.ini` explicit files: 2 passed all versions; `--lf` no last-failed (autouse leak does not fail). Collapsed nodeids do not create last-failed here. No View/export.

Leftover `--ff` after `-c config/pytest.ini` explicit files: 2 passed all versions; `--ff` no last-failed. Autouse leak does not fail. No View/export.

Leftover `--nf` after `-c config/pytest.ini` explicit files: **2 passed** both runs on 8.4.1–9.1.1. Autouse leak does not fail. No View/export.
