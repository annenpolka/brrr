# Host 実機 pytest#14608 invocation-dir `tests/`

Not Dreamer-facing. HOLD no View. PR #14622/#14624 not applied.

Public layout from the PR's regression test (not the PR diff applied):

- `tests/conftest.py` registers `--db-url`
- `test_it.py` at the invocation dir reads `request.config.getoption("--db-url")`
- command: `pytest --db-url scheme://host/db` with **no file args and no testpaths**

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 1 passed |
| 9.0.1 | 0 | 1 passed |
| 9.0.3 | 0 | 1 passed |
| 9.1.0 | 4 | unrecognized arguments `--db-url` |
| 9.1.1 | 0 | 1 passed |

Explicit `pytest --db-url ... tests test_it.py` is rc=0 on 8.4.1/9.1.0/9.1.1 (path args load the conftest). The 9.1.0 miss is **initial** conftest load of `<invocation dir>/test*` when no path is given.

Controls (same `--db-url` command, no file args):

| layout | 8.4.1 | 9.0.3 | 9.1.0 | 9.1.1 |
| --- | --- | --- | --- | --- |
| `test_foo/conftest.py` | pass | pass | unrecognized | pass |
| `testing/conftest.py` | pass | pass (9.0.1/9.0.3 too) | unrecognized | pass |
| `test/conftest.py` | pass | pass (9.0.1/9.0.3 too) | unrecognized | pass |
| `src/conftest.py` | unrecognized | unrecognized | unrecognized | unrecognized |
| invocation-dir `conftest.py` (not under `test*`) | pass | pass | **pass** | pass |
| nested `tests/unit/conftest.py` | unrecognized | unrecognized | unrecognized | unrecognized |
| `tests/test_it.py` inside `tests/` (no root test) | pass | pass | unrecognized | pass |
| `Tests/conftest.py` (capital T) | unrecognized | (not run) | unrecognized | unrecognized |
| `test-foo/` (hyphen) | pass | pass (9.0.1/9.0.3 too) | unrecognized | pass |
| `testdir/` | pass | pass (9.0.1/9.0.3 too) | unrecognized | pass |
| `testfoo/` (unique tree) | pass | pass | unrecognized | pass |
| `testing123/` | pass | (not run) | unrecognized | pass |
| `test_suite/` | pass | (not run) | unrecognized | pass |
| `test2/` | pass | (not run) | unrecognized | pass |
| `mytests/` | unrecognized | (not run) | unrecognized | unrecognized |
| `_tests/` | unrecognized | unrecognized | unrecognized | unrecognized |

9.0.1 matches 8.4.1/9.0.3 on these two layouts. Root `conftest.py` is initial on **every** version including 9.1.0. Nested `tests/unit/` is never initial, including 8.4.1/9.1.1. The 9.1.0-only miss is a **direct** invocation-dir `test*` child.

`testpaths` leftover (command still `pytest --db-url ...`, no file args):

| ini | 8.4.1 / 9.0.1 / 9.0.3 / 9.1.1 | 9.1.0 |
| --- | --- | --- |
| `testpaths = tests` | rc=5 no tests ran (`test_it.py` outside `tests/`; `--db-url` recognized) | rc=4 unrecognized `--db-url` |
| `testpaths = other` (missing) | rc=0 1 passed + PytestConfigWarning (recursive fallback) | rc=4 unrecognized `--db-url` |

`testpaths = tests` does **not** rescue 9.1.0: option parse still happens before that conftest is initial.

`confcutdir = .` leftover: `--db-url` still unrecognized on 9.1.0; 8.4.1/9.0.1/9.0.3/9.1.1 pass (warning). confcutdir does not rescue 9.1.0.

CLI path order leftover (same tree):

| command | 8.4.1 / 9.0.1 / 9.1.1 | 9.1.0 |
| --- | --- | --- |
| `pytest tests --db-url ...` | rc=5 no tests ran (`--db-url` recognized) | rc=5 same (rescued) |
| `pytest --db-url ... tests` | rc=5 `--db-url` recognized | rc=5 rescued |
| `pytest test_it.py --db-url ...` | rc=4 unrecognized | rc=4 unrecognized |
| `pytest --db-url ... test_it.py` | rc=4 unrecognized | rc=4 unrecognized |

A CLI `tests` path loads that conftest as initial even on 9.1.0. A CLI `test_it.py` file does not, on any version. The 9.1.0-only miss is **no file args** (auto `test*` under the invocation dir).

Leftover pythonpath (command still `pytest --db-url ...`, no file args):

| setting | 8.4.1 / 9.0.1 / 9.0.3 / 9.1.1 | 9.1.0 |
| --- | --- | --- |
| `pythonpath = tests` (`pytest.ini`) | rc=0 1 passed | rc=4 unrecognized `--db-url` |
| `pythonpath = .` | rc=0 1 passed | rc=4 unrecognized |
| `[tool.pytest.ini_options] pythonpath = ["tests"]` | rc=0 1 passed | rc=4 unrecognized |
| `-o pythonpath=tests` | rc=0 1 passed | rc=4 unrecognized |

pythonpath does **not** rescue 9.1.0. It is not initial-conftest load.

Leftover `addopts = tests` (ini path arg):

| layout | 8.4.1–9.1.1 including 9.1.0 |
| --- | --- |
| `test_it.py` at root | rc=5 no tests ran; `--db-url` recognized |
| `tests/test_it.py` inside `tests/` | rc=0 1 passed |

Ini path args rescue 9.1.0 the same way CLI `tests` does.

Leftover `PYTEST_ADDOPTS=tests` (env path arg, no file args): same as ini `addopts = tests`. Root `test_it.py`: rc=5 no tests ran, `--db-url` recognized including 9.1.0. `tests/test_it.py` inside `tests/`: rc=0 1 passed including 9.1.0. Env path args rescue 9.1.0 the same way CLI/ini path args do.

Leftover `-o addopts=tests` (CLI ini override, no file args, root `test_it.py`): rc=5 no tests ran on 8.4.1–9.1.1 including 9.1.0; `--db-url` recognized (not unrecognized). Same rescue as ini/CLI/env path args.

Leftover `-o addopts=tests` on `alt_inside` (`tests/test_it.py` inside `tests/`): **1 passed** on 8.4.1–9.1.1 including 9.1.0. CLI `-o addopts=` rescues 9.1.0 the same way ini/env path args do when the test lives under that path.

Leftover `confcutdir = tests`: `--db-url` still unrecognized on 9.1.0; 8.4.1/9.0.1/9.0.3/9.1.1 pass (warning). Same as `confcutdir=.`.

Leftover `--noconftest`: unrecognized `--db-url` on **all** of 8.4.1–9.1.1. The option comes from conftest `pytest_addoption`.

Leftover `norecursedirs = tests`: 9.1.0 still unrecognized; other versions still 1 passed (`test_it.py` at root). Recursion skip does not change initial `test*` conftest load.

Leftover `pythonpath = tests` with `tests/test_it.py` inside `tests/` (no addopts): still 9.1.0 unrecognized; 8.4.1/9.0.1/9.0.3/9.1.1 1 passed. Same as `alt_inside` without pythonpath.

Leftover `collect_ignore = tests`: 9.1.0 still unrecognized; other versions 1 passed (root `test_it.py`) + warning. collect_ignore does not stop initial `test*` conftest load.

Leftover `consider_namespace_packages = true`: 9.1.0 still unrecognized; 8.4.1/9.0.1/9.0.3/9.1.1 1 passed. Does not rescue 9.1.0.

`src/` is not a `test*` name; it is never an initial conftest here. Sibling `A/`+`B/` sketches did not show this split.

Leftover `--collect-only --db-url` (isolated `alt_lo_base/`): same 9.1.0-only unrecognized (rc=4); 8.4.1/9.0.1/9.0.3/9.1.1 **1 collected**. Collect-only does not skip the miss.

Leftover CLI `--confcutdir=.` / `--import-mode=importlib` / `--rootdir=.` / `python_files = test_it.py`: still 9.1.0 unrecognized; other versions 1 passed. None of these rescue 9.1.0.

Leftover named `pytest.toml` `[pytest] addopts = "tests"` (string): 8.4.1 unread **1 passed** (default `tests/` initial). Pytest 9 rc=1 TypeError `addopts` expects a list, got str. Leftover list form `addopts = ["tests"]`: 8.4.1 unread 1 passed; pytest 9 rc=5 no tests ran (`--db-url` recognized; `test_it.py` outside `tests/`). List form rescues 9.1.0 the same way ini/CLI/env path args do.

Leftover native `[tool.pytest] addopts = ["tests"]` (root `test_it.py`): 8.4.1 unread 1 passed; pytest 9 rc=5 no tests ran (rescues 9.1.0). Leftover same native with `tests/test_it.py` inside `tests/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. Native path args rescue 9.1.0 like ini `addopts = tests`.

Leftover `--setup-show --db-url` on isolated `alt_lo_base/`: same 9.1.0-only unrecognized (rc=4); 8.4.1/9.0.1/9.0.3/9.1.1 **1 passed**. `--setup-show` does not skip the miss. Still HOLD; no View/export. Repair SHAs stay off Dreamer.

Leftover `--override-ini addopts=tests` on `alt_lo_base/` (tests/ has conftest only): rc=5 no tests all versions (does not rescue). Leftover `--override-ini addopts=test_it.py --db-url x` on `alt_lo_base/`: unrecognized `--db-url` **all versions** (file path does not load `tests/conftest.py`). Leftover `--override-ini addopts=tests --db-url x` on `alt_inside/`: **rescues 9.1.0** (1 collected including 9.1.0; dummy value `x` fails the assert, option is known). Same rescue family as `-o addopts=tests` / CLI `tests` path. No View/export.

Leftover `--override-ini addopts=tests --db-url scheme://host/db` on `alt_inside/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. Confirms the path-arg rescue with the option value the test asserts. No View/export.

Leftover `--lf`/`--ff`/`--sw` with the same `--override-ini addopts=tests --db-url scheme://host/db` on `alt_inside/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0 (no last-failed). No View.

Leftover `--nf` with the same rescue on `alt_inside/`: **1 passed** on 8.4.1–9.1.1 including 9.1.0. No View.

Leftover `alt_lo_base/` `--lf`/`--ff`/`--nf`/`--sw --db-url scheme://host/db`: 8.4.1–9.0.3/9.1.1 **1 passed**; 9.1.0 rc=4 unrecognized both runs. The 9.1.0 miss is not last-failed. No View.

Leftover `alt_lo_base/` `--maxfail=1 --db-url scheme://host/db`: same 9.1.0 unrecognized both runs. `--maxfail=1` does not skip the option miss. No View.

Leftover `--noconftest --db-url x` on `alt_lo_base/`: unrecognized `--db-url` **all versions**. `--noconftest` skips the option-defining conftest. No View/export.
Leftover-0566 `alt_lo_base/` `-c /dev/null --db-url scheme://host/db`: 8.4.1/9.0.1/9.0.3/9.1.1 **1 passed**; **9.1.0 rc=4 unrecognized** (`inifile: /dev/null`, `rootdir: /dev`). `/dev/null` does **not** rescue 9.1.0. Leftover-0569 `alt_inside/` same split. Leftover-0587 `--config-file=/dev/null` same.

Leftover-0692 `alt_inside/` `--override-ini addopts=tests -c /dev/null --db-url` and `--config-file=/dev/null`: **1 passed all including 9.1.0** (leftover-0251 rescue **survives `/dev/null`**). Same flags on `alt_lo_base/`: **rc=5 all** (`addopts=tests` loads `tests/conftest.py` so `--db-url` is recognized; `test_it.py` is outside `tests/`). HOLD no View.

Leftover-0695 later `-o addopts=--strict-config` **overwrites** leftover-0251 `--override-ini addopts=tests` after `/dev/null`: **9.1.0 unrecognized --db-url** (rescue lost); **9.1.1 leftover-0476 unknown verbosity**. env `PYTEST_ADDOPTS='-o addopts=tests' -c /dev/null`: **1 passed including 9.1.0**. cwd pytest.ini `addopts=tests` **displaced** by `/dev/null` (leftover-0566 9.1.0 unrecognized). CLI `--strict-config -o verbosity=2` **pytest 9 all rc=4** hides rescue.

Leftover-0698 leftover-0251 vs leftover-0476 **last addopts wins** after `/dev/null`: later `--override-ini addopts=tests` or later `-o addopts=tests` **rescues 9.1.0**; later `-o addopts=--strict-config` **loses rescue**. `-o addopts=tests -c /dev/null` **1 passed including 9.1.0**. leftover-0251 + `-o verbosity=2` without `--strict-config` **1 passed all** with pytest 9 warning. HOLD no View.

