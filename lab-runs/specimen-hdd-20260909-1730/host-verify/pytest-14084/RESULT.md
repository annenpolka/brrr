# Host 実機 pytest#14084

Not Dreamer-facing. HOLD no View. Do not apply the PR.

`amodule/tests` has `__init__.py`. `--pyargs amodule.tests`.

| cwd / PYTHONPATH | 8.4.1 | 9.0.1 | 9.1.1 |
| --- | --- | --- | --- |
| package root, `PYTHONPATH=.` | rc=0 1 pass | rc=0 | rc=0 (9.0.3/9.1.0 also 0) |
| `subdir/`, `PYTHONPATH=..` | rc=0 1 pass | rc=0 | rc=0 (9.0.3/9.1.0 also 0) |
| `subdir/`, `PYTHONPATH=.` | rc=4 `missing __init__.py?` | rc=4 | rc=4 (9.0.3/9.1.0 also 4) |
| `subdir/`, no PYTHONPATH | rc=4 same | rc=4 | rc=4 |

From a subdirectory, `--pyargs` still needs the parent on PYTHONPATH. Same on 8.4 and 9.x.

Leftover `subdir/` `PYTHONPATH=.` on 9.0.3/9.1.0: rc=4 `missing __init__.py?` (same as 8.4.1/9.0.1/9.1.1). Leftover `--collect-only --pyargs` from `subdir/`: `PYTHONPATH=..` **1 collected** all versions; `PYTHONPATH=.` rc=4 all. Collect-only matches run. No View/export.

Leftover package-root `PYTHONPATH=. --lf`/`--ff --pyargs amodule`: **1 passed** on 8.4.1–9.1.1. No last-failed. No View.

Leftover package-root `PYTHONPATH=. --nf`/`--sw --pyargs amodule`: **1 passed** on 8.4.1–9.1.1. No View.

Leftover-0713 `PYTHONPATH=. -c /dev/null --pyargs amodule.tests` and subdir `PYTHONPATH=.. -c /dev/null`: **1 passed all**. subdir `PYTHONPATH=.` or no PYTHONPATH `-c /dev/null`: **rc=4** missing `__init__.py` all. leftover-14084 PYTHONPATH rescue **survives `/dev/null`**.

Leftover-0716 leftover-0476 + `PYTHONPATH=.` or subdir `PYTHONPATH=..`: leftover-0476 weaker split **hides rescue on 9.1.0+**. leftover-0476 verbosity without `--strict-config` **1 passed all**. HOLD no View.
