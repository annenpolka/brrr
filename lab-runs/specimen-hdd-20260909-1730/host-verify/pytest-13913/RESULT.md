# Host 実機 pytest#13913

Not Dreamer-facing. HOLD no View. No sqlalchemy clone.

Mini: `pyproject.toml` has `testpaths = ["tests"]` and `python_files = "test_*.py"` (string). `tests/conftest.py` registers `--db` and `--write-idents`. `tests/test_it.py`. `idents.txt` exists at root.

| argv | 8.4.1 | 9.0.1 | 9.0.3 | 9.1.0 | 9.1.1 |
| --- | --- | --- | --- | --- | --- |
| `--db sqlite --write-idents idents.txt` | rc=0 1 pass | rc=4 unrecognized `--db --write-idents` | rc=4 | rc=4 | rc=4 |
| `--db sqlite --write-idents nosuch-idents-file` | rc=0 | rc=0 | rc=0 | rc=4 unrecognized | rc=0 |
| `tests --db sqlite --write-idents idents.txt` | rc=0 | rc=0 | rc=0 | rc=0 | rc=0 |
| `--db sqlite` (no write-idents) | rc=0 | rc=0 | rc=0 | rc=4 unrecognized `--db` | rc=0 |

Same `--db sqlite --write-idents idents.txt` split when `python_files` is a list, when `python_files` is omitted, and when `addopts = "--tb=line -q"` is added: 8.4.1 rc=0, pytest 9 rc=4 unrecognized. The string vs list `python_files` and extra addopts are not the cause.

With `testpaths`, 8.4.1 loads `tests/conftest.py` even when `idents.txt` exists. Pytest 9 does not (existing file as option value). Explicit `tests/` always loads the options.

Leftover `pythonpath = ["tests"]` next to `testpaths`: `--db sqlite --write-idents idents.txt` still 8.4.1 rc=0 1 pass; pytest 9 (9.0.1–9.1.1) rc=4 unrecognized `--db --write-idents`. pythonpath does not rescue the existing-file option-value miss.

Leftover `--collect-only --db sqlite --write-idents idents.txt`: 8.4.1 **1 collected**; pytest 9 rc=4 unrecognized. Collect-only still hits the existing-file option-value miss.

Leftover `--setup-show tests/`: **1 passed** on 8.4.1–9.1.1. Explicit `tests/` path does not hit `--write-idents`. No View/export.

Leftover `--tb=short --db sqlite --write-idents idents.txt tests/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. Explicit `tests/` path still rescues the option (same as `--setup-show tests/`). No View.

Leftover `--tb=short --db sqlite --write-idents idents.txt` (no `tests/` path): 8.4.1 **1 passed**; pytest 9 rc=4 unrecognized `--db --write-idents`. Same 8/9 option miss as collect-only without a path arg. Explicit `tests/` still rescues. No View.

Leftover `--setup-plan --db sqlite --write-idents idents.txt tests/`: **1 collected** on 8.4.1–9.1.1 including 9.1.0. Explicit `tests/` still rescues at plan. No tests ran. No View.

Leftover `--setup-plan --db sqlite --write-idents idents.txt` (no path): 8.4.1 **1 collected**; pytest 9 rc=4 unrecognized `--db --write-idents`. Same 8/9 option miss as collect-only / `--tb=short` without a path arg. No View.

Leftover no-path `--lf`/`--ff`/`--sw --db sqlite --write-idents idents.txt`: 8.4.1 **1 passed**; pytest 9 rc=4 unrecognized `--db --write-idents`. Same 8/9 option miss; unrecognized is not last-failed. No View.

Leftover `tests/` `--ff`/`--sw --db sqlite --write-idents idents.txt tests/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. Explicit path still rescues. No View.

Leftover `tests/` `--lf`/`--nf --db sqlite --write-idents idents.txt tests/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. No View.
Leftover-0701 no-path `-c /dev/null --db sqlite --write-idents idents.txt`: 8.4.1 **rc=2** parent leftover dummy `--db` collisions (`addopts/tests`, `alt_pp/tests`, …) after `testpaths` displaced (`rootdir: /dev`); pytest 9 **rc=4 unrecognized** `--db --write-idents` (`inifile: /dev/null`, `rootdir: /dev`). Explicit `tests/` `-c /dev/null` and `--config-file=/dev/null`: **1 passed all including 9.1.0** (leftover-13913 `tests/` rescue **survives `/dev/null`**). HOLD no View.

Leftover-0704 isolated no-path `-c /dev/null`: **8.4.1 1 passed** / pytest 9 **rc=4 unrecognized** (leftover-0701 8.4.1 rc=2 was leftover-dir `--db` collisions). Isolated `tests/` `-c /dev/null` **1 passed all**. leftover-0476 + `tests/` **9.1.0+ rc=4 hides rescue**. leftover-0251 `--override-ini addopts=tests -c /dev/null` **1 passed all**. Later `-o addopts=--strict-config` loses rescue (pytest 9 unrecognized). Later `--override-ini addopts=tests` / env `addopts=tests` **wins**.

Leftover-0707 isolated leftover-0251 last-wins: later `--override-ini addopts=tests` **1 passed all**; later `-o addopts=--strict-config` **8.4.1 1 passed** / pytest 9 unrecognized (no leftover-dir collisions). `tests/` + `-o verbosity=2` without `--strict-config` **1 passed all** with pytest 9 warning. `-o addopts=tests -c /dev/null` **1 passed all**. HOLD no View.

