# Host 実機 pytest#13479

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

pytest 8.4.1 + freezegun 1.5.2 on the public snippet: setup error `fixture 'ff' not found`. Matches the reported 8.4 regression.
- pytest 9.0.1+freezegun: rc=1 `fixture 'ff' not found`
- pytest 9.0.3+freezegun: rc=1 `fixture 'ff' not found`
- pytest 9.1.0+freezegun: rc=1 `fixture 'ff' not found`
- pytest 9.1.1+freezegun: rc=1 (host refute; still HOLD, no View)

Leftover `--setup-show`: no SETUP `ff`; ERROR `fixture 'ff' not found` on 8.4.1–9.1.1. `--setup-show` does not change the missing class-fixture registration.

Leftover `--collect-only test_freeze.py`: **1 collected** on 8.4.1–9.1.1. Missing `ff` is execute, not collect. No View.

Leftover `--setup-plan test_freeze.py`: 1 collected then ERROR `fixture 'ff' not found` at setup on 8.4.1–9.1.1. Missing `ff` is visible at plan. No View.

Leftover `--lf` / `--ff` / `--sw`: still **1 error** `fixture 'ff' not found` on 8.4.1–9.1.1. Last-failed / stepwise rerun does not register the class fixture. No View.
