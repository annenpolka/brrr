# Host 実機 pytest#13755 further-minimized comment snippet

Not Dreamer-facing. HOLD no View.

Session `fix_once` + `test_a` then `test_b` with overlapping params. `--setup-show`:

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 1 | test_a 2 pass; test_b 2 ERROR `assert 'a' not in {'a', 'b'}`. Session fixture torn down after test_a then re-setup |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |

Same 8/9. Session cache does not span `test_a` → `test_b` in this mini. `--setup-show` counts **4 SETUP S / 4 TEARDOWN S** `fix_once` on 8.4.1 and 9.1.1. Original `pytest-13755` 4 params / 10 setups still HOLD.

Leftover `--setup-plan`: no tests ran; printed plan is **4 SETUP S / 4 TEARDOWN S** on 8.4.1–9.1.1 including 9.1.0. Plan already shows `fix_once['a']` torn down before `fix_once['b']`. Same as execute. No View/export.

Leftover `--collect-only`: **4 collected** on 8.4.1–9.1.1. Same-param re-setup ERROR is execute, not collect. No View/export.

Leftover `--lf` after session-teardown ERROR: seed **2 passed, 2 errors**; `--lf` **2 passed, 2 deselected** on 8.4.1–9.1.1. Rerunning only the failed `test_b` params skips `test_a`, so `fix_once` is not torn down between. `--lf` hides the session-teardown miss. No View/export.

Leftover `--ff`: seed 2 pass 2 error on `test_b`; `--ff` then **2 passed, 2 errors on `test_a`**. Failed-first runs `test_b` first (now pass) then remaining `test_a` ERROR. Miss still visible, swapped onto `test_a`. No View/export.

Leftover `--sw`: first run interrupted at first `test_b` error (2 pass 1 error). Second `--sw` **2 passed, 2 deselected**. Hides the remaining `test_b` error like `--lf`. No View/export.

Leftover `--nf`: still **2 passed, 2 errors** both runs. `--nf` does not hide the session-teardown miss. No View/export.

Leftover `--maxfail=1`: **2 passed, 1 error** (`test_b[a-x]` only). Hides the second `test_b` param error. First error is still the miss. No View/export.
