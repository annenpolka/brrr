# Host 実機 pytest#14445

Not Dreamer-facing. HOLD no View.

Walrus in rewritten assertions.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | 2 failed (`1 != 1`; `count == 6` not 3) |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same (reporter's version) |
| 9.1.0 | 1 | same (`1 != 1`; `6 == 3`) |
| 9.1.1 | 1 | same |
| 8.4.1 `--assert=plain` | 0 | 2 passed |
| 9.0.1 `--assert=plain` | 0 | 2 passed |
| 9.0.3 `--assert=plain` | 0 | 2 passed |
| 9.1.0 `--assert=plain` | 0 | 2 passed |
| 9.1.1 `--assert=plain` | 0 | 2 passed |
| native Python 3.14 (no pytest) | 0 | both asserts pass (`count == 3`) |

Leftover `--tb=short`: still **2 failed** on 8.4.1–9.1.1 (`1 != 1`; `6 == 3`). Traceback style does not change walrus double-eval.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. Double-eval is execute rewrite, not collect. No View.

Leftover `--tb=line`: still **2 failed** (`1 != 1`; `6 == 3`) on 8.4.1–9.1.1. Line traceback does not change walrus double-eval. No View.

No View/export. Related rewrite PRs stay 正解 off Dreamer.
