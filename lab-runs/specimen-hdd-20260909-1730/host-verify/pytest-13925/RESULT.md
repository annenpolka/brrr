# Host 実機 pytest#13925

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public layout: `test_root.py` (`1/0`) plus `a/test_a.py`; command `pytest -q '' a/`.
- pytest 8.4.1: rc=0, 1 passed (`""` did not collect `test_root.py`)
- pytest 9.0.1: rc=2, ERROR collecting `test_root.py` ZeroDivisionError
- pytest 9.0.3: rc=2 same ZeroDivisionError collect
- pytest 9.1.0: rc=2 same ZeroDivisionError collect
- pytest 9.1.1: rc=2 same

Matches reporter's pytest 8 vs 9 discovery change.

Leftover controls (8.4.1/9.0.1/9.1.1):
- `pytest -q ''` alone: rc=2 collect `test_root.py` ZeroDivisionError **all versions** (`''` is cwd)
- `pytest -q .` same ZeroDivisionError all versions
- `pytest -q a/` 1 passed all versions

The 8 vs 9 delta is specifically `'' a/` together: 8.4.1 ignores `''` when another path is given.

`--collect-only -q '' a/`: 8.4.1 1 collected (`a/test_a.py` only); 9.1.1 1 collected + ERROR `test_root.py` ZeroDivisionError. Same split as run mode. No View staged.

Leftover reverse `a/ ''`: same split (8.4.1 1 passed; pytest 9 ZeroDivision collecting `test_root.py`). `--collect-only '' a/`: 8.4.1 collects `a/test_a` only; pytest 9 collects `a/test_a` and errors on `test_root.py`. empty/dot/aonly on 9.0.3/9.1.0 match the other versions. `pytest -q -- a/` is 1 passed on 8.4.1–9.1.1 (`--` is not an empty path).

Leftover `a/ .` and `. a/`: same 8.4.1 1 passed / pytest 9 ZeroDivision split. 8.4.1 ignores overlapping cwd `.` when a subdirectory path is also given (same family as 12083 overlapping-dir drop). `.` alone still ZeroDivision on all versions.

Leftover `--keep-duplicates '' a/` and `--keep-duplicates a/ .`: **ZeroDivision collecting `test_root.py` on 8.4.1–9.1.1** (rc=2 all). `--keep-duplicates` restores the dropped overlapping cwd on 8.4.1, so the 8/9 split disappears.

Leftover `'' .` and `. ''`: ZeroDivision collecting `test_root.py` on **8.4.1–9.1.1** (rc=2 all). Both args are cwd, so 8.4.1 cannot drop an overlapping extra path; the 8/9 split needs a **subdirectory** next to cwd/`''`.

Leftover `--keep-duplicates '' .` and `--collect-only '' .`: still **ZeroDivision** collecting `test_root.py` on 8.4.1–9.1.1 (rc=2). Collect-only lists `a/test_a.py::test_foo` plus the root error. `--keep-duplicates` does not change two cwd args.

Leftover same-dir twice `a/ a/`: collect/run **1** unique all versions (`test_foo` only; `test_root.py` not under `a/`). `--keep-duplicates a/ a/`: n=**2** / 2 passed all.

Leftover same-empty twice `'' ''`: ZeroDivision collecting `test_root.py` on **8.4.1–9.1.1** (rc=2). `--collect-only` lists `a/test_a.py::test_foo` plus the root error. `--keep-duplicates '' ''` still ZeroDivision. Two empty args are both cwd, same as `'' .`.

Leftover same-dot twice `. .`: ZeroDivision all versions (rc=2). `--collect-only` 1 collected + 1 error. `--keep-duplicates . .`: **2 errors** collecting `test_root.py` (cwd duplicated). `--keep-duplicates --collect-only '' ''`: n=**2** (`test_foo` twice) + 2 errors all versions. No View.

Leftover `--setup-plan a/`: 1 item all versions (no ZeroDivision). Leftover `--setup-plan '' a/`: 8.4.1 n=**1** (cwd dropped, no ZeroDivision at plan); pytest 9 collect ERROR ZeroDivision `test_root.py`. Same 8/9 cwd-overlap split as execute. No View.

Leftover `--setup-plan . a/`: 8.4.1 n=**1** (cwd dropped); pytest 9 collect ERROR ZeroDivision `test_root.py`. Same as `'' a/`. No View.

Leftover `--setup-plan --keep-duplicates . a/`: **2 collected / 1 error** ZeroDivision `test_root.py` on **8.4.1 too** (and pytest 9). Keep-duplicates restores the dropped overlapping cwd at plan, same as execute. No View.

Leftover `--setup-plan a/ a/` (same dir twice): n=**1** unique all versions (no ZeroDivision; `a/` is the passing dir). No View.

Leftover `--setup-plan --keep-duplicates a/ a/`: n=**2** all versions (no ZeroDivision). Same as collect. No View.

Leftover `--setup-plan -- a/`: n=**1** on 8.4.1–9.1.1 (no ZeroDivision). `--` does not reintroduce cwd `test_root.py`. Same as `pytest a/`. No View.

Leftover `--setup-plan --keep-duplicates -- a/`: n=**1** all versions. Keep-duplicates of a single `-- a/` path does not restore cwd. No View.
