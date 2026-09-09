# Host 実機 pytest#14819

Not Dreamer-facing. HOLD no View.

Chained comparison `1 < 0 < 1/0` and `1 < 0 < boom()` under assertion rewriting.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | 2 failed (`ZeroDivisionError`; `calls == ['boom']`) |
| 9.0.1 | 1 | 2 failed (same) |
| 9.0.3 | 1 | 2 failed (same) |
| 9.1.0 | 1 | 2 failed (same) |
| 9.1.1 | 1 | 2 failed (same) |
| 8.4.1 `--assert=plain` | 1 | first `AssertionError` (short-circuit); second passed |
| 9.0.1 `--assert=plain` | 1 | same |
| 9.0.3 `--assert=plain` | 1 | same |
| 9.1.0 `--assert=plain` | 1 | same |
| 9.1.1 `--assert=plain` | 1 | first `AssertionError` (short-circuit); second passed |
| native Python 3.14 (no pytest) | 0 | both `AssertionError`; `boom` not called |

Rewrite does not short-circuit the later operand.

Leftover `--tb=short`: still **2 failed** on 8.4.1–9.1.1 (`ZeroDivisionError` + `boom` called). Traceback style does not change the rewrite.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. The miss is execute rewrite, not collect. No View/export.

Leftover `--lf`/`--ff`/`--nf`: still **2 failed** (ZeroDivision + boom) on 8.4.1–9.1.1. `--sw` first run 1 fail interrupted; second still 1 fail (hides boom). `--maxfail=1` **1 failed** (hides boom). `--assert=plain` **1 failed, 1 passed** (short-circuit; boom not called) on 8.4.1–9.1.1; `--lf` then 1 fail. No View/export.
