# Host 実機 pytest#14095

Not Dreamer-facing. HOLD no View.

pytest 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=1. Class-level fixture `a` does not rebuild module-scoped `b` (`assert 0 == 1`).

Leftover `--setup-show` 8.4.1/9.0.3/9.1.0/9.1.1: SETUP module `a` then `b` (uses `a`), then TestClass SETUP `a`, TEARDOWN TestClass `a`, TEARDOWN `b`, TEARDOWN first `a`. `b` stays 0 not 1. Same all versions (family of #5203).

Leftover `--collect-only test_a.py`: **2 collected** on 8.4.1–9.1.1. The miss is execute (`b` not rebuilt), not collect. No View.

Leftover `--setup-plan test_a.py`: same as 5203 — SETUP M `b` uses first module `a` on 8.4.1–9.1.1. No tests ran. No View.

Leftover `--lf` after rebuild miss: seed **1 failed, 1 passed**; `--lf` **1 passed, 1 deselected** on 8.4.1–9.1.1. Same as #5203: skipping the first module hides the miss. No View.

Leftover `--ff`: miss **swaps onto `test_b_is_zero`** (`assert 1 == 0`). Same family as #5203 `--ff`. No View.

Leftover `--nf`: still original `TestClass::test_b_is_one` fail. `--nf` does not hide. No View.

Leftover `--sw`: second run **1 passed, 1 deselected**. Hides the miss like `--lf`. No View.

Leftover `--maxfail=1`: still **1 failed, 1 passed** (miss visible). No View.
