# Host 実機 pytest#13704 `a/b a/` ordering

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public layout: `a/test_a.py`, `a/b/test_b.py`, `a/a/test_aa.py`.

| pytest | `a/b a/` | `a/` | `a/ a/b` |
| --- | --- | --- | --- |
| 8.4.1 | collect **1** (`test_b` only; parent dropped) | collect **3** | collect **1** (`test_b` only) |
| 9.0.1 | collect **3** (`test_aa`, `test_b`, `test_a`) | 3 | 3 |
| 9.0.3 | 3 | 3 | 3 |
| 9.1.0 | 3 | 3 | 3 |
| 9.1.1 | 3 | 3 | 3 |

On pytest 9, `a/b a/` is equivalent to `a/` (same 3 tests). Order is `test_aa` then `test_b` then `test_a`: `a/b` is **not** ordered before `a/a`. Matches the PR. 8.4.1 still drops the overlapping parent (family of #12083).

Leftover `--keep-duplicates a/b a/`: n=4 on 8.4.1–9.1.1 (`test_b`, `test_aa`, `test_b`, `test_a`). Leftover `--keep-duplicates a/ a/b`: n=4 all (`test_aa`, `test_b`, `test_a`, `test_b`). `--keep-duplicates` restores the overlapping parent tests on 8.4.1 and doubles `test_b` on pytest 9.

Leftover **run** `a/b a/`: 8.4.1 **1 passed** (`test_b` only); pytest 9 **3 passed**. Matches collect.

Leftover **run** reverse `a/ a/b`: same 8.4.1 **1 passed** / pytest 9 **3 passed**. Leftover `--keep-duplicates a/ a/b` **run**: **4 passed** on 8.4.1–9.1.1 (same as keep-duplicates collect).

Leftover `a/a a/` and `a/ a/a`: 8.4.1 collect/run **1** (`test_aa` only; parent dropped). Pytest 9 **3** (`test_aa`, `test_b`, `test_a`). Same overlapping-parent drop as `a/b a/`. Leftover `--keep-duplicates a/a a/`: n=**4** all versions (`test_aa` twice + `test_b` + `test_a`). Leftover `--keep-duplicates a/a a/` **run**: **4 passed** all versions.

Leftover sibling `a/a a/b` and reverse `a/b a/a`: collect/run **2** (`test_aa` + `test_b`) on **8.4.1–9.1.1**. `--keep-duplicates` still n=**2** / 2 passed (no overlapping parent to restore). 8.4.1 parent-drop is **parent-only**, not sibling overlap.

Leftover same-dir twice `a/ a/`: collect/run **3** unique on **all** versions (unlike same-file twice 2 vs 1). `--keep-duplicates a/ a/`: n=**6** / 6 passed all. Same directory twice unique-unions; `--keep-duplicates` doubles the tree.

Leftover file-vs-parent `a/a/test_aa.py a/` and reverse `a/ a/a/test_aa.py`: 8.4.1 collect/run **1** (`test_aa` only; parent dropped). Pytest 9 **3**. Same family as #13704 dir/file. `--keep-duplicates`: n=**4** / 4 passed all (`test_aa` twice + `test_b` + `test_a`).

Leftover file-vs-sibling-dir `a/a/test_aa.py a/b`: collect/run **2** on **all** versions. `--keep-duplicates` still n=**2**. No ancestor, no drop.

Leftover file-in-parent `a/test_a.py a/`: 8.4.1 collect/run **1** (`test_a` only; parent dropped). Pytest 9 **3**. `--keep-duplicates` n=**4** / 4 passed (`test_a` twice). Same family as #13704 dir/file.

Leftover two files `a/a/test_aa.py a/test_a.py`: n=**2** all versions; `--keep-duplicates` still n=**2**. Distinct files do not overlap.

Leftover cwd-as-parent `a/b .`: same as `a/b a/` (8.4.1 n=1 / pytest 9 n=3; `--keep-duplicates` n=4; run 1 vs 3). `.` collects the same `a/` tree.

Leftover file-vs-cwd `a/a/test_aa.py .`: same as `a/a/test_aa.py a/` (8.4.1 n=1 / pytest 9 n=3; `--keep-duplicates` n=4).

Leftover child-dir vs cwd `a/a .`: same as `a/a a/` (8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4; run 1 vs 3). `.` is the overlapping parent of `a/a`.

Leftover file vs **containing dir** `a/a/test_aa.py a/a`: collect/run **1** all versions; `--keep-duplicates` n=**2**. No 8/9 split (dir has only that file). Leftover parent-file vs child-dir `a/test_a.py a/a`: n=**2** all (`test_a` + `test_aa`); keep still 2. Not ancestor overlap. No View/export.

Leftover `--setup-plan a/b a/` and reverse `a/ a/b`: 8.4.1 n=**1** / pytest 9 n=**3**. Leftover `--keep-duplicates a/b a/`: n=**4** all. Same overlap as collect/run. No tests ran. No View.

Leftover `--setup-plan a/a/test_aa.py .`: 8.4.1 n=**1** / pytest 9 n=**3**. Same file-vs-cwd drop as collect. No tests ran. No View.

Leftover `--setup-plan --keep-duplicates a/ a/`: n=**6** on 8.4.1–9.1.1. Same as collect keep-duplicates. No tests ran. No View.

Leftover `--setup-plan a/ a/` (same dir twice, unique): n=**3** on 8.4.1–9.1.1. Same unique-union as collect/run. No tests ran. No View.
