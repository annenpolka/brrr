# Host 実機 pytest#14048

Not Dreamer-facing. HOLD no View.

`PYTHONPATH=. pytest --pyargs amodule.tests` without `amodule/tests/__init__.py`.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 4 | `module or package not found: amodule.tests (missing __init__.py?)` |
| 9.0.1 | 4 | same |
| 9.0.3 | 4 | same |
| 9.1.0 | 4 | same |
| 9.1.1 | 4 | same |
| 8.4.1 with `tests/__init__.py` | 0 | 1 passed |
| 9.0.1 with `tests/__init__.py` | 0 | 1 passed |
| 9.0.3 with `tests/__init__.py` | 0 | 1 passed |
| 9.1.0 with `tests/__init__.py` | 0 | 1 passed |
| 9.1.1 with `tests/__init__.py` | 0 | 1 passed |

Matches the reporter's pytest line, not the tox/3.14.2 wrapper. Adding `amodule/tests/__init__.py` makes `--pyargs` collect.

Leftover `--collect-only --pyargs amodule.tests` (current tree **has** `tests/__init__.py`): **1 collected** on 8.4.1–9.1.1. Leftover `--import-mode=importlib` same 1 collected all versions. importlib does not replace the missing-`__init__.py` requirement in the noinit runs. No View/export.

Leftover `--setup-show --pyargs amodule.tests` without PYTHONPATH: rc=4 `module or package not found: amodule.tests (missing __init__.py?)` on 8.4.1–9.1.1 even with `tests/__init__.py` present. Leftover `PYTHONPATH=. --setup-show --pyargs amodule.tests`: **1 passed** all versions. `--pyargs` still needs PYTHONPATH (or equivalent) to import the package. No View/export.

Leftover `PYTHONPATH=. --lf`/`--ff`/`--nf`/`--sw --pyargs amodule`: **1 passed** on 8.4.1–9.1.1 (no last-failed). No View.

Leftover `PYTHONPATH=. --maxfail=1 --pyargs amodule`: **1 passed** on 8.4.1–9.1.1. No View.
Leftover-0710 `PYTHONPATH=. -c /dev/null --pyargs amodule.tests` and `--config-file=/dev/null`: **1 passed all**. Without PYTHONPATH `-c /dev/null --pyargs`: **rc=4** `module or package not found: amodule.tests (missing __init__.py?)` all versions. leftover-14048 PYTHONPATH rescue **survives `/dev/null`**. HOLD no View.

Leftover-0713 leftover-0476 + `PYTHONPATH=. -c /dev/null --pyargs`: leftover-0476 weaker split **hides PYTHONPATH rescue on 9.1.0+**. CLI `--strict-config verbosity` **pytest 9 all rc=4**. leftover-0476 no PYTHONPATH: 8.4.1/9.0.x missing `__init__.py` / 9.1.0+ unknown verbosity. `-o`/`--override-ini pythonpath=.` **does not rescue --pyargs** (rc=4 all). leftover-0476 verbosity without `--strict-config` **1 passed all**. leftover-14048 `PYTHONPATH=. --pyargs amodule -c /dev/null` **1 passed all**. HOLD no View.

