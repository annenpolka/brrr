# Host 実機 pytest#14691

Not Dreamer-facing. HOLD no View.

Class-scoped `@classmethod` fixture `sample` is not collected.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | ERROR `fixture 'sample' not found` |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |
| 8.4.1 fixture without `@classmethod` | 0 | 1 passed |
| 9.1.1 fixture without `@classmethod` | 0 | 1 passed |
| 9.1.1 `@staticmethod` fixture | 0 | 1 passed |

Failure is the `@classmethod` + fixture combination.

Leftover `--setup-show test_classmethod.py`: no SETUP `sample`; ERROR `fixture 'sample' not found` on 8.4.1–9.1.1. The classmethod is never registered as a fixture.

Leftover `--collect-only test_classmethod.py`: **1 collected** on 8.4.1–9.1.1. Missing fixture is execute, not collect.

Leftover without `@classmethod` (`no_cm/`): 9.0.1/9.0.3 **1 passed**; 9.1.0 **1 passed, 1 warning** (class-scoped instance-method deprecation). Same as 8.4.1/9.1.1 already recorded. No View/export.

Leftover `--setup-plan test_classmethod.py`: 1 collected then ERROR `fixture 'sample' not found` at setup on 8.4.1–9.1.1. Requested missing fixture errors at plan (like #14971). No View.

Leftover `--lf` / `--ff`: still **1 error** `fixture 'sample' not found` on 8.4.1–9.1.1. Last-failed rerun does not register the classmethod fixture. No View.
