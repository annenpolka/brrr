# Host 実機 pytest#14964

Not Dreamer-facing. HOLD for HDD consumer (no View/export). Reporter's source-cause notes stay off the Dreamer channel.

Public layout: `test_x.py` + `tests/{__init__.py,conftest.py autouse guard, a.py, b.py}`.

CASE1 `pytest tests/a.py test_x.py tests/b.py`:
- pytest 8.4.1 / 9.0.1 / 9.0.3: rc=1, test_a and test_b ERROR `guard ran` (1 passed, 2 errors)
- pytest 9.1.0 / 9.1.1: rc=1, test_a ERROR `guard ran`; test_b PASSES (2 passed, 1 error)

CASE2 `pytest tests/a.py tests/b.py test_x.py` and CASE3 `pytest test_x.py tests/a.py tests/b.py`:
- pytest 8.4.1 / 9.0.1 / 9.1.1: both tests under `tests/` ERROR `guard ran`

Matches the reporter's 9.1.1 interleaved-only miss.

Leftover reverse CASE1 `tests/b.py test_x.py tests/a.py`: 8.4.1–9.0.3 both a and b ERROR `guard ran`; 9.1.0/9.1.1 only **test_b** (first) ERROR, later **test_a PASSES** (guard missed). Same interleaved-only miss.

Leftover `--setup-show` CASE1: 8.4.1/9.0.3 SETUP `guard` for both tests. 9.1.0/9.1.1 SETUP `guard` for test_a only, then test_b never gets the autouse (passes).

Leftover `pytest tests` (default python_files): rc=5 no tests ran on 8.4.1–9.1.1 (`a.py`/`b.py` are not `test_*.py`). Leftover `pytest tests/a.py tests/b.py` (no gap): **both** ERROR `guard ran` on 8.4.1–9.1.1. Leftover `python_files = *.py` + `pytest tests`: both ERROR `guard ran` all versions. Leftover `tests/a.py test_x.py` and `test_x.py tests/b.py` (one tests/ file + gap): **1 error** `guard ran` on 8.4.1–9.1.1 (no later-test miss). The 9.1.0 miss requires **two** `tests/` files with a gap **between** them.

Leftover `--keep-duplicates` CASE1: still 8.4.1–9.0.3 both ERROR; 9.1.0/9.1.1 later `test_b` PASSES (2 passed, 1 error). `--keep-duplicates` does **not** restore the autouse miss. Leftover `--collect-only` CASE1: n=**3** all versions (miss is execute-only). `--keep-duplicates --collect-only` still n=3 (distinct files).

Leftover `--setup-plan` CASE1: 8.4.1–9.0.3 lists `fixtures used: guard` for **both** a and b. 9.1.0/9.1.1 lists guard for **test_a only**; later `tests/b.py::test_b` has no guard. The miss is visible at **plan**, not only execute.

Leftover `--setup-plan` reverse: 8.4.1–9.0.3 guard for both; 9.1.0/9.1.1 guard for **test_b only**, later `test_a` listed without guard (rc=0). Leftover 14964d `--setup-plan` gap: same (guard for first only from 9.1.0).

Leftover `--lf` after CASE1 (isolated cache): 8.4.1–9.0.3 reruns **both** errors. 9.1.0/9.1.1 reruns **only test_a** (1 error); the later test that PASSed (missed guard) is not last-failed. `--lf` hides the later miss.

Leftover `--ff` after CASE1: 8.4.1–9.0.3 1 pass 2 errors (failed first then remaining). 9.1.0/9.1.1 `E..` 2 pass 1 error (failed-first test_a, then test_x and later test_b PASS). `--ff` still shows the later miss as PASS (unlike `--lf`).

Leftover `--maxfail=1` CASE1: all versions stop after test_a error (`stopping after 1 failures`). Hides later error on 8.4.1 and hides later PASS (miss) on 9.1.0.

Leftover `--lf --lfnf none`: same as `--lf` when last-failed exist (8.4.1 both errors; 9.1.0 only test_a). Bare `--lfnf` without `--lf` is UsageError rc=4.

Leftover `--nf` after CASE1: 8.4.1 1 pass 2 errors (later error still present). 9.1.0/9.1.1 `.E.` 2 pass 1 error (later test_b still PASS). `--nf` does **not** hide the later miss (unlike `--lf`).

Leftover `--sw` after CASE1: all versions stop at test_a error (`Interrupted: Test failed, continuing from this test next run`). Second `--sw` still stuck on test_a. Hides later miss like `--maxfail=1`. No View staged.
