# Host 実機 pytest#7777 nested package collection

Not Dreamer-facing. HOLD no View. Related #11646/#13704 stay 正解 off Dreamer.

Public tree: nested `a/b/c/d` packages; `c` has no `__init__.py`.

`pytest --collect-only a/` and `--keep-duplicates a/` on 8.4.1–9.1.1:

- collected **5** items
- nested `<Package a> / <Package b> / <Dir c> / <Package d>` (not the pytest-6 flat Packages)
- `--keep-duplicates` still **5** (no Session+Package duplicate items)

The pytest-6 `--keep-duplicates` 11-item duplication is gone after the collection rework. No 8/9 delta.

Leftover `pytest --collect-only a/b`: n=3 on 8.4.1–9.1.1 (`test_d`, `test_c`, `test_b`). Leftover `a/b/c`: n=2 (`test_d`, `test_c`). Nested `Dir c` (no `__init__.py`) still collects.

Leftover `a/b a/` and `a/ a/b`: 8.4.1 n=3 (parent `a/` dropped; only `a/b` subtree). Pytest 9 n=5 (full `a/` including `a/b2` and `a/test_a`). Same overlapping-parent drop as #13704b.

Leftover **run** `a/b a/` and `a/ a/b`: 8.4.1 **3 passed**; pytest 9 **5 passed**. Matches collect.

Leftover `--keep-duplicates a/b a/` **run**: **8 passed** on 8.4.1–9.1.1 (`a/b` subtree twice + `a/b2` + `a/test_a`). Leftover `--keep-duplicates a/ a/b` **run**: same **8 passed** all versions. Restores the dropped parent on 8.4.1 and doubles the overlapping subtree on pytest 9.

Leftover package-scoped fixtures (pytest-7777b, smaller `a/{b,b2}` tree): `--setup-show -s a/` **3 passed** 8.4.1–9.1.1. `pkg_a` SETUP once; `pkg_b` SETUP/TEARDOWN around `test_b1` only. No 8/9 delta.

Leftover `a/b2 a/` and `a/ a/b2`: 8.4.1 collect/run **1** (`test_b21` only; parent dropped). Pytest 9 **5**. Leftover `--keep-duplicates a/b2 a/` **run**: **6 passed** all versions (`test_b21` twice + the other four). That argv still includes parent `a/`.

Leftover sibling `a/b a/b2` and reverse `a/b2 a/b` (**no parent**): collect/run **4** on **8.4.1–9.1.1** (`test_d1`, `test_c1`, `test_b1`, `test_b21`). `--keep-duplicates` still n=**4** / 4 passed. 8.4.1 does **not** drop a sibling subtree.

Leftover same-dir twice `a/ a/`: collect/run **5** unique all versions. `--keep-duplicates a/ a/`: n=**10** / 10 passed all. Same directory twice unique-unions; keep-duplicates doubles the nested tree.

Leftover nested ancestor `a/b/c a/` and reverse: 8.4.1 collect/run **2** (`test_d1`/`test_c1` only; parent dropped). Pytest 9 **5**. `--keep-duplicates`: n=**7** / 7 passed all (c subtree twice + the other three). Ancestor drop works through nested `Dir c` (no `__init__.py`).

Leftover nested vs mid-parent `a/b/c a/b`: 8.4.1 **2** / pytest 9 **3**. `--keep-duplicates` n=**5**. Mid-parent drop too.

Leftover nested vs sibling `a/b/c a/b2`: **3** all versions. `--keep-duplicates` still n=**3**. No ancestor, no drop.

Leftover deepest nested `a/b/c/d a/`: 8.4.1 collect/run **1** (`test_d1` only). Pytest 9 **5**. `--keep-duplicates` n=**6** / 6 passed. Ancestor drop works at any depth.

Leftover cwd-as-parent `a/b/c .`: same as `a/b/c a/` (8.4.1 n=2 / pytest 9 n=5; `--keep-duplicates` n=7; run 2 vs 5). `.` collects the same `a/` tree. No View/export.

Leftover `a/b/c/d a/b`: 8.4.1 **1** / pytest 9 **3**; keep-duplicates n=**4**. Leftover `a/b/c/d a/b/c`: 8.4.1 **1** / pytest 9 **2**; keep-duplicates n=**3**. Leftover `a/b/c/d a/b2`: **2** all versions; keep-duplicates still n=**2**.

Leftover file-vs-cwd `a/test_a.py .`: 8.4.1 collect/run **1** (`test_a1` only). Pytest 9 **5**. `--keep-duplicates`: n=**6** / 6 passed (`test_a1` twice + the other four). Same as file-in-parent vs `a/`.

Leftover nested file-vs-ancestor `a/b/c/d/test_d.py a/`: same as dir `a/b/c/d a/` (8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6). Vs mid `a/b`: 1 vs 3 / keep 4. Vs Dir `a/b/c`: 1 vs 2 / keep 3. File-vs-cwd `a/b/c/d/test_d.py .` and dir-vs-cwd `a/b/c/d .`: same 1 vs 5 / keep 6. Nested file vs ancestor still drops the parent on 8.4.1.

Leftover nested file vs sibling `a/b/c/d/test_d.py a/b2`: collect/run **2** all versions; `--keep-duplicates` still n=**2**. No ancestor, no drop.

Leftover nested file vs **containing dir** `a/b/c/d/test_d.py a/b/c/d`: collect/run **1** (`test_d1`) on **8.4.1–9.1.1**. `--keep-duplicates` n=**2** (same test twice). No 8/9 parent-drop: the dir has no extra tests beyond the file.

Leftover two files different depths `a/b/c/d/test_d.py a/test_a.py`: n=**2** all; keep still 2. Leftover two files sibling-branch `a/b/c/d/test_d.py a/b2/test_b2.py`: n=**2** all. Distinct files do not overlap. No View/export.

Leftover `--setup-plan a/b a/`: 8.4.1 n=**3** (parent dropped); pytest 9 n=**5**. Same overlap as collect/run. No tests ran. No View/export.

Leftover `--setup-plan` reverse `a/ a/b`: 8.4.1 n=**3** / pytest 9 n=**5**. Leftover `--keep-duplicates a/b a/`: n=**8** all. Same as run overlap. No tests ran. No View/export.

Leftover `--setup-plan a/test_a.py .`: 8.4.1 n=**1** / pytest 9 n=**5**. Same file-vs-cwd drop as collect. No tests ran. No View/export.

Leftover `--setup-plan a/ a/` (same dir twice): n=**5** unique all versions. Same as collect. No tests ran. No View/export.

Leftover `--setup-plan --keep-duplicates a/ a/`: n=**10** on 8.4.1–9.1.1. Same as collect keep-duplicates. No tests ran. No View/export.

Leftover `--setup-plan a/b2 a/`: 8.4.1 n=**1** / pytest 9 n=**5**. Same overlap drop as collect. No tests ran. No View/export.

Leftover `--setup-plan --keep-duplicates a/b2 a/`: n=**6** on 8.4.1–9.1.1. Keep-duplicates restores the dropped parent on 8.4.1 and doubles `test_b21` on pytest 9. Same as keep-duplicates run. No View/export.
