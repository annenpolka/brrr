# Host 実機 pytest#14964 `test_*.py` names dir vs interleaved gap

Not Dreamer-facing. HOLD no View.

Same autouse-guard layout as #14964, but files are `tests/test_a.py` / `tests/test_b.py` (default `python_files`).

| pytest | `pytest tests` | `tests/test_a.py test_x.py tests/test_b.py` (gap) | `tests/test_a.py tests/test_b.py` (no gap) |
| --- | --- | --- | --- |
| 8.4.1 | both ERROR `guard ran` | both ERROR + test_x pass | both ERROR |
| 9.0.3 | both ERROR | both ERROR + test_x pass | both ERROR |
| 9.1.0 | both ERROR | test_a ERROR; **test_b PASSES** (2 passed, 1 error) | both ERROR |
| 9.1.1 | both ERROR | same miss | both ERROR |

The 9.1.0 interleaved-gap miss is **not** because the original files were named `a.py`/`b.py`. Directory collect and no-gap still apply the guard on 9.1.0.

Leftover reverse `tests/test_b.py test_x.py tests/test_a.py`: 8.4.1–9.0.3 both ERROR; 9.1.0/9.1.1 only **test_b** (first) ERROR, later **test_a PASSES**. Same interleaved-gap miss. 9.0.1 same as 8.4.1 (2 errors).

Leftover `--setup-show` gap: 8.4.1/9.0.3 SETUP `guard` for both tests. 9.1.0/9.1.1 SETUP `guard` for test_a only, then test_b never gets the autouse (passes). Same as #14964.

Leftover `--setup-show` reverse gap: 8.4.1–9.0.3 SETUP `guard` for both; 9.1.0/9.1.1 SETUP `guard` for **test_b** (first) only, later **test_a PASSES**. Leftover `--setup-show` directory collect and no-gap: SETUP `guard` for **both** on 8.4.1–9.1.1 (2 errors). Directory/no-gap still apply the guard on 9.1.0.

Leftover `--keep-duplicates` gap: still 8.4.1–9.0.3 both ERROR; 9.1.0/9.1.1 later `test_b` PASSES. Collect-only gap n=**3** all. `--keep-duplicates` does not restore the miss.

Leftover `--lf` after gap: 8.4.1–9.0.3 reruns **both** errors. 9.1.0/9.1.1 reruns **only test_a** (later PASS not last-failed). Same as #14964. No View/export.

Leftover `--ff` after gap: 8.4.1–9.0.3 seed 2 errors; `--ff` reruns both first, still 2 errors. 9.1.0/9.1.1 seed later test PASSES; `--ff` reruns test_a first then **both** tests/ files ERROR (1 passed, 2 errors). `--ff` does not hide the later miss the way `--lf` does; failed-first reorder makes the later test error too. No View/export.

Leftover `--maxfail=1` CASE1: **1 error** (`test_a` only) on 8.4.1–9.1.1. First-test ERROR stops the run, so the later miss is never observed (and 8.4.1's second error is hidden too). Unlike #14640/#14971 `--maxfail=1` where earlier tests pass so the later miss still shows. No View/export.

Leftover `--nf` after gap: 8.4.1–9.0.3 both errors still. 9.1.0/9.1.1 seed later PASS; `--nf` then **both** tests/ files ERROR (1 passed, 2 errors). `--nf` does not hide the later miss the way `--lf` does (same family as `--ff`). No View/export.

Leftover `--sw` after gap: all versions stop at `test_a` guard ERROR (`Interrupted`). Second `--sw` still stuck on `test_a`. Hides later miss like `--maxfail=1` and like #14964 `--sw`. No View/export.
