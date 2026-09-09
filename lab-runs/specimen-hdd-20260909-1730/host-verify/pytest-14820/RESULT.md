# Host 実機 pytest#14820

Not Dreamer-facing. HOLD no View.

Assertion rewrite reads a name after a later call rebinds it.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | `test_left_operand_is_read_too_late` fail (`99 == 0`); second test pass |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |
| 8.4.1 `--assert=plain` | 0 | 2 passed |
| 9.0.1 `--assert=plain` | 0 | 2 passed |
| 9.0.3 `--assert=plain` | 0 | 2 passed |
| 9.1.0 `--assert=plain` | 0 | 2 passed |
| 9.1.1 `--assert=plain` | 0 | 2 passed |
| native Python 3.14 (no pytest) | 0 | both asserts pass (`0 == 0` after evaluating left then `bump`) |

Leftover `--tb=short`: same 1 failed / 1 passed on 8.4.1–9.1.1 (`99 == 0`; `where 0 = bump_count()`). Traceback style does not change the rewrite.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. The miss is execute rewrite, not collect. No View/export. PR SHAs stay off Dreamer.

Leftover `--tb=line`: still **1 failed, 1 passed** (`99 == 0`) on 8.4.1–9.1.1. Line traceback does not change the rewrite. No View.
