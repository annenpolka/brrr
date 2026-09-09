# Host 実機 pytest#13704 overlapping collection arguments

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public layout: `tests/test_it.py`, `tests/test_other.py`.

| pytest | `tests/ tests/test_it.py` | `tests/test_it.py tests/` | `tests/test_it.py` twice |
| --- | --- | --- | --- |
| 8.4.1 | collect 1 / run 1 pass (`test_it` only) | collect 1 | collect 2 / run 2 pass |
| 9.0.1 | collect 2 / run 2 pass | collect 2 | collect 1 / run 1 pass |
| 9.0.3 | 2 | 2 | 1 |
| 9.1.0 | 2 | 2 | 1 |
| 9.1.1 | 2 | 2 | 1 |

Matches the PR: pytest 8 overlap keeps only the nested file; pytest 9 collects the whole dir. Same file twice runs twice on 8.4.1, once on pytest 9. Same family as #12083.

Leftover `--keep-duplicates tests/ tests/test_it.py`: n=3 on 8.4.1–9.1.1 (`test_it`, `test_other`, `test_it`). Run of that argv: **3 passed** on 8.4.1–9.1.1. Leftover `--keep-duplicates tests/test_it.py tests/test_it.py`: n=2 all versions. `--keep-duplicates` restores the pytest-8 overlap triple and the same-file double on pytest 9.

Leftover `--keep-duplicates tests/test_it.py tests/` collect: n=3 all (`test_it` twice + `test_other`). Leftover **run** of that argv: **3 passed** on 8.4.1–9.1.1. Reverse keep-duplicates matches the original triple.

Leftover same-dir twice `tests/ tests/`: collect/run **2** unique on **all** versions (`test_it` + `test_other`). `--keep-duplicates tests/ tests/`: n=**4** / 4 passed all. Same directory twice unique-unions (no 8/9 split). The 8.4.1 double vs pytest-9 single is **same file twice**, not same directory twice.

Leftover file-vs-parent `tests/test_other.py tests/` and reverse `tests/ tests/test_other.py`: 8.4.1 collect/run **1** (`test_other` only; parent dropped). Pytest 9 **2**. `--keep-duplicates tests/test_other.py tests/`: n=**3** / 3 passed all (`test_other` twice + `test_it`). Same family as `tests/test_it.py tests/`. Leftover two distinct files `tests/test_other.py tests/test_it.py`: n=**2** all versions.

Leftover three-way `tests/test_it.py tests/test_other.py tests/`: collect/run **2** unique on **all** versions (both files cover the tree; 8.4.1 parent drop is hidden). `--keep-duplicates`: n=**4** / 4 passed all.

Leftover `tests/test_it.py tests .`: 8.4.1 collect **1** (`test_it` only; parent/cwd dropped so `test_other` gone). Pytest 9 **2**. One explicit file does not hide the 8/9 split.

Leftover file-vs-cwd `tests/test_it.py .`: 8.4.1 collect/run **1** (`test_it` only). Pytest 9 **2**. `--keep-duplicates`: n=**3** / 3 passed all. Same as file-vs-parent with `tests/` (cwd collects the same tree). No View/export.

Leftover `--setup-plan tests/ tests/test_it.py`: 8.4.1 n=**1**; pytest 9 n=**2**. Same overlap drop as collect. No tests ran. No View.

Leftover `--setup-plan` reverse `tests/test_it.py tests/`: 8.4.1 n=**1** / pytest 9 n=**2**. Leftover `--keep-duplicates tests/ tests/test_it.py`: n=**3** all. Same overlap as collect. No tests ran. No View.

Leftover `--setup-plan tests/test_it.py tests/test_it.py` (same file twice): 8.4.1 n=**2** / pytest 9 n=**1**. Same unique-union as collect. No tests ran. No View.

Leftover `--setup-plan tests/ tests/` (same dir twice): n=**2** unique all versions. Leftover `--keep-duplicates tests/ tests/`: n=**4** all. Same as collect. No tests ran. No View.

Leftover `--setup-plan tests/test_it.py tests .`: 8.4.1 n=**1** / pytest 9 n=**2**. Same overlapping-parent drop as collect three-way. No tests ran. No View.

Leftover `--setup-plan --keep-duplicates tests/test_it.py tests .`: n=**5** on 8.4.1–9.1.1. Keep-duplicates restores the dropped parent plus cwd. No View.
