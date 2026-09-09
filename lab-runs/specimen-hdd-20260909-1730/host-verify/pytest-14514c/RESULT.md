# Host 実機 pytest#14514 top-level `foo.test.py`

Not Dreamer-facing. HOLD feature. No View.

File is at the collection root (no package).

| pytest | default | `--import-mode=importlib` |
| --- | --- | --- |
| 8.4.1 | rc=2 `ModuleNotFoundError: No module named 'foo'` | rc=0 1 passed |
| 9.0.1 | rc=2 same | rc=0 |
| 9.0.3 | rc=2 same | rc=0 |
| 9.1.0 | rc=2 same | rc=0 |
| 9.1.1 | rc=2 same | rc=0 |

Same importlib workaround as the packaged `pkg/foo.test.py` case.

Leftover `--collect-only` no file args: rc=5 (default `python_files` skips `foo.test.py`). Leftover explicit `foo.test.py`: rc=2 `No module named 'foo'` on 8.4.1–9.1.1; `--import-mode=importlib` **1 collected**. Same as run.

Leftover `--setup-show --import-mode=importlib foo.test.py`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not change importlib. No View/export.

Leftover `--tb=short --import-mode=importlib foo.test.py`: **1 passed** on 8.4.1–9.1.1. Importlib still collects the dotted filename. No View.

Leftover `--tb=short foo.test.py` (default import mode): collect ImportError on 8.4.1–9.1.1. `--tb=short` does not replace `--import-mode=importlib`. No View.

Leftover `--setup-plan foo.test.py` (default import mode): collect ImportError on 8.4.1–9.1.1. Plan does not replace `--import-mode=importlib`. No View.

Leftover `--lf`/`--ff`/`--sw --import-mode=importlib foo.test.py`: **1 passed** on 8.4.1–9.1.1. Importlib collect is not last-failed. No View.

Leftover `--lf`/`--ff`/`--sw foo.test.py` (default import): collect ImportError both runs on 8.4.1–9.1.1. Collect-error is not last-failed. Leftover importlib `--nf`: **1 passed**. No View.
