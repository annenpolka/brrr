# Host 実機 pytest#14694

Not Dreamer-facing. HOLD no View. Do not apply the PR. No xclim tree.

Mini: `src/pkg/testing/conftest.py` injects `doctest_namespace["ANSWER"]=42`; `src/pkg/mod.py` doctest reads `ANSWER`. Collect parent package while `--rootdir` is the testing subdirectory.

| argv | 8.4.1 | 9.0.1 | 9.0.3 | 9.1.0 | 9.1.1 |
| --- | --- | --- | --- | --- | --- |
| `--rootdir src/pkg/testing --doctest-modules src/pkg` | rc=0 1 pass | rc=0 | rc=0 | rc=1 `NameError: ANSWER` | rc=1 `NameError: ANSWER` |
| `--rootdir src/pkg --doctest-modules src/pkg` | rc=1 NameError | rc=1 | rc=1 | rc=1 | rc=1 |
| `--doctest-modules src/pkg` (no extra rootdir) | rc=1 NameError | rc=1 | rc=1 | rc=1 | rc=1 |

Matches the reporter's 9.0.3 pass / 9.1.1 fail for the `--rootdir` subdirectory case. 14683 stripped doctest (no `--rootdir` split) still passed all versions.

Leftover `pythonpath = src/pkg/testing` with the same `--rootdir src/pkg/testing --doctest-modules src/pkg`: still 1 pass on 8.4.1–9.0.3 and `NameError: ANSWER` on 9.1.0/9.1.1. pythonpath does not restore the doctest namespace.

Leftover `--setup-show --rootdir src/pkg/testing --doctest-modules src/pkg`: 8.4.1/9.0.1/9.0.3 SETUP S `doctest_namespace` then SETUP F `add_answer` (uses doctest_namespace), 1 passed. 9.1.0/9.1.1 SETUP S `doctest_namespace` only — **no SETUP F `add_answer`** — then NameError `ANSWER`. The 9.1.0 miss is the injecting fixture not set up, not a doctest rewrite change. No View/export. PR stays 正解 off Dreamer.

Leftover `--collect-only --rootdir src/pkg/testing --doctest-modules src/pkg`: **1 collected** on 8.4.1–9.1.1 including 9.1.0. NameError `ANSWER` is execute (injecting fixture not set up), not collect. No View/export.

Leftover `--tb=short --rootdir src/pkg/testing --doctest-modules src/pkg`: 8.4.1–9.0.3 **1 passed**. 9.1.0/9.1.1 NameError `ANSWER`. Short traceback does not restore the injecting fixture. No View/export.
