# Host 実機 pytest#7777 package-scoped fixtures

Not Dreamer-facing. HOLD no View. Related #11646/#13704 stay 正解 off Dreamer.

Public nested packages `a/{b,b2}` with `__init__.py`. Package-scoped `pkg_a` on `a/conftest.py`, `pkg_b` on `a/b/conftest.py`. `pytest --setup-show -s a/` on 8.4.1–9.1.1:

- collected **3** items, **3 passed**, rc=0
- `SETUP P pkg_a` once before `a/b/test_b.py::test_b1`
- `SETUP P pkg_b` only for `test_b1`; `TEARDOWN P pkg_b` immediately after
- `a/b2/test_b2.py::test_b21` and `a/test_a.py::test_a1` use `pkg_a` only
- `TEARDOWN P pkg_a` after the last test in package `a`

No 8/9 delta. Package scope still nests (inner `pkg_b` does not tear down `pkg_a`). Collection of this smaller tree is 3, not the 5-item `a/b/c/d` tree in pytest-7777.

Leftover `a/b a/` collect/run: 8.4.1 **1** (`a/b` only; parent dropped); pytest 9 **3**. Leftover `--keep-duplicates a/b a/`: **4** on 8.4.1–9.1.1. Same overlapping-parent drop as pytest-7777. No View/export.

Leftover file-vs-cwd `a/test_a.py .` and `a/b .`: 8.4.1 n=**1** (cwd dropped) / pytest 9 n=**3**. Leftover `--keep-duplicates a/test_a.py .`: n=**4** all (`test_a` twice). Same overlapping-parent drop family as pytest-7777. No View/export.

Leftover `--setup-plan a/b a/` and `a/test_a.py .`: 8.4.1 n=**1** / pytest 9 n=**3**. Plan lists `pkg_a`/`pkg_b` for the collected subset. Same overlapping-parent drop as collect. No View/export.

Leftover `--setup-plan --keep-duplicates a/b a/`: n=**4** on 8.4.1–9.1.1. Same as collect keep-duplicates. No tests ran. No View/export.

Leftover `--setup-plan a/ a/b` reverse: 8.4.1 n=**1** / pytest 9 n=**3**. Same overlap drop as collect. No tests ran. No View/export.

Leftover `--setup-plan a/b2 a/`: 8.4.1 n=**1** / pytest 9 n=**3**. Same overlapping-parent drop as `a/b a/` collect. No tests ran. No View/export.

Leftover `--setup-plan --keep-duplicates a/b2 a/`: n=**4** on 8.4.1–9.1.1. Keep-duplicates restores the dropped parent on 8.4.1 and doubles `test_b21` on pytest 9. Same family as keep `a/b a/`. No View/export.
