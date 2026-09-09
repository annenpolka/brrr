# Host 実機 pytest#12083 overlapping collection args

Not Dreamer-facing. HOLD no View. Related PR #13704 stays 正解 off Dreamer.

Public layout: `tests/test_one.py`, `tests/subdirectory/test_two.py`.
Command: `pytest --collect-only tests/test_one.py tests`

| pytest | overlap (`test_one.py tests`) | `--keep-duplicates` same args | `tests` only |
| --- | --- | --- | --- |
| 8.4.1 | rc=0 **1** (`test_one` only; subdirectory dropped) | rc=0 **3** (test_one twice + test_two) | rc=0 **2** |
| 9.0.1 | rc=0 **2** (test_two + test_one) | 3 | 2 |
| 9.0.3 | 2 | 3 | 2 |
| 9.1.0 | 2 | 3 | 2 |
| 9.1.1 | 2 | 3 | 2 |

Matches the reporter's pytest-8 drop of the overlapping directory. Pytest 9 collects both unique tests. `--keep-duplicates` restores the pytest-7 triple.

Leftover reverse `tests tests/test_one.py`: same split (8.4.1 n=1 `test_one` only; pytest 9 n=2). Leftover `tests/subdirectory tests`: 8.4.1 n=1 `test_two` only (parent `tests` dropped); pytest 9 n=2. Run (not collect-only) overlap: 8.4.1 1 passed; pytest 9 2 passed. 8.4.1 drops the overlapping directory regardless of argv order.

Leftover `--keep-duplicates tests tests/test_one.py`: n=3 on 8.4.1–9.1.1 (same as original keep-duplicates). Leftover `--keep-duplicates tests/subdirectory tests`: n=3 all versions (`test_two` twice + `test_one`). Leftover two file args `tests/test_one.py tests/subdirectory/test_two.py` (no overlapping dirs): n=2 on all versions. Leftover `tests .` and `. tests`: n=2 unique on **all** versions (cwd adds no extra tests). The 8/9 delta is overlapping directory vs file when the extra path would collect additional tests (see 13925 `a/ .`). `--keep-duplicates` run: 3 passed on 8.4.1 and 9.1.1.

Leftover `--keep-duplicates tests .`: n=**4** on 8.4.1–9.1.1 (`test_one`/`test_two` twice). Leftover **run** of that argv: **4 passed** all versions. Leftover `--keep-duplicates . tests` reverse: n=4 all. Without `--keep-duplicates`, cwd unique-unions to 2; with it, cwd duplicates `tests/`.

Leftover same-dir twice `tests tests`: collect/run **2** unique on **all** versions. `--keep-duplicates tests tests`: n=**4** / 4 passed all. Same directory twice unique-unions (no 8/9 split); keep-duplicates doubles both tests.

Leftover same-subdir twice `tests/subdirectory tests/subdirectory`: collect/run **1** unique all (`test_two` only). `--keep-duplicates`: n=**2** / 2 passed all. Same unique-union as same-dir twice.

Leftover `tests/subdirectory .` and reverse `. tests/subdirectory`: 8.4.1 collect/run **1** (`test_two` only; parent cwd dropped). Pytest 9 **2** (`test_two` + `test_one`). `--keep-duplicates`: n=**3** / 3 passed all (`test_two` twice + `test_one`). Leftover `tests/subdirectory ''`: same 8.4.1 n=1 / pytest 9 n=2. `--keep-duplicates tests/subdirectory ''`: n=3 all. This is the 8/9 cwd-as-parent split that `tests .` did not show (`tests/` is the whole cwd collection).

Leftover three-way `tests/subdirectory tests/test_one.py .`: collect/run **2** unique on **all** versions (8.4.1 keeps the explicit file, so the 8/9 cwd-drop disappears). `--keep-duplicates`: n=**4** / 4 passed all (subdir + file + cwd duplicates both). Adding a file arg that covers the extra cwd test hides the 8.4.1 parent drop.

Leftover three dirs `tests/subdirectory tests .`: 8.4.1 collect **1** (`test_two` only; both parents dropped). Pytest 9 **2**. `--keep-duplicates`: n=**5** all (`test_two` three times + `test_one` twice). Directory-only overlapping parents still 8/9.

Leftover file-vs-cwd `tests/test_one.py .`: 8.4.1 collect/run **1** (`test_one` only; cwd dropped). Pytest 9 **2**. `--keep-duplicates`: n=**3** / 3 passed all (`test_one` twice + `test_two`). Same family as file-vs-parent. No View/export.

Leftover `--setup-plan tests/test_one.py tests`: 8.4.1 n=**1**; pytest 9 n=**2**. Same overlapping-dir drop as collect/run. No tests ran. No View.

Leftover `--setup-plan` reverse `tests tests/test_one.py`: 8.4.1 n=**1** / pytest 9 n=**2**. Leftover `--setup-plan --keep-duplicates tests/test_one.py tests`: n=**3** all versions. Same overlap split as collect. No tests ran. No View.

Leftover `--setup-plan tests/subdirectory .`: 8.4.1 n=**1** / pytest 9 n=**2**. Same cwd-as-parent drop as collect. No tests ran. No View.

Leftover `--setup-plan --keep-duplicates tests/subdirectory .`: n=**3** all versions. Keep-duplicates restores the dropped cwd on 8.4.1 at plan too. No View.

Leftover `--setup-plan tests tests` (same dir twice): n=**2** unique all. Leftover `--keep-duplicates tests tests`: n=**4** all. Same as collect. No tests ran. No View.

Leftover `--setup-plan tests/subdirectory tests`: 8.4.1 n=**1** / pytest 9 n=**2**. Same parent-drop as collect. No tests ran. No View.

Leftover `--setup-plan --keep-duplicates tests/subdirectory tests`: n=**3** all versions. Keep-duplicates restores the dropped parent at plan. No View.

Leftover `--setup-plan tests/subdirectory tests/test_one.py .`: n=**2** on 8.4.1–9.1.1. Adding the file hides the 8/9 cwd-overlap split at plan (same as collect three-way). No tests ran. No View.

Leftover `--setup-plan --keep-duplicates tests/subdirectory tests/test_one.py .`: n=**4** on 8.4.1–9.1.1. Keep-duplicates restores cwd even when a file arg hid the 8/9 split. No View.
