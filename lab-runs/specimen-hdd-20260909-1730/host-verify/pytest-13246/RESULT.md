# Host 実機 pytest#13246 sibling conftest fixture shadow

Not Dreamer-facing. HOLD no View. Do not apply PR #14837. Did not clone the reporter's full tree.

Public layout: `config/pytest.ini`; `tests/tests1` fixture `value=1`; `tests/tests2` fixture `value=2`.

Command: `pytest -c config/pytest.ini tests/tests2/test2.py::test2 tests/tests1/test1.py::test1`

| pytest | `-c config/pytest.ini` | same + `--rootdir=.` |
| --- | --- | --- |
| 8.4.1 | rc=1; `FAILED config::test2 - assert 1 == 2` | rc=0 2 passed |
| 9.0.1 | same | rc=0 |
| 9.0.3 | same | rc=0 |
| 9.1.0 | same | rc=0 |
| 9.1.1 | same | rc=0 |

Matches the reporter: first-collected `value` is reused; `--rootdir=.` restores local fixtures.

Invoked from `subdir/` with `-c ../config/pytest.ini`: still `FAILED ../config::test2 - assert 1 == 2` on 8.4.1/9.1.1.

Leftover `--setup-show -c config/pytest.ini` same argv: SETUP `value` for test2 (FAIL 1==2) then SETUP `value` for test1 (PASS) on 8.4.1–9.1.1. `--setup-show` does not restore local fixtures. No View/export.

Leftover `--collect-only -c config/pytest.ini` same argv: **2 collected** on 8.4.1–9.1.1. Sibling `value` shadow is execute, not collect. No View/export.

Leftover `--tb=short -c config/pytest.ini` same argv: still 1 failed 1 passed (sibling `value` shadow) on 8.4.1–9.1.1. Short traceback does not restore local fixtures. No View/export.

Leftover `--setup-plan -c config/pytest.ini` same argv: 2 collected, SETUP F `value` for both tests, on 8.4.1–9.1.1. Plan lists both fixtures; sibling shadow (`1 == 2`) is execute. No tests ran. No View/export.

Leftover `--lf` / `--ff` / `--nf`: still **1 failed, 1 passed** sibling `value` shadow on 8.4.1–9.1.1. `--sw` stuck on first fail both runs. `--maxfail=1` **1 failed** (hides the later pass, not the miss). Last-failed rerun does not restore local fixtures. No View/export.
