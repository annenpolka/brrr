# Host 実機 pytest#5203

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public module-scoped fixture override snippet (`a=4` vs class `a=3`).
- pytest 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1: rc=1, `TestB.test_b` assert 8 == 6 (`b` not rebuilt)

Same symptom family as 14095.

Leftover `--setup-show` 8.4.1/9.1.0/9.1.1: SETUP module `a` then `b` (uses `a`), then TestB SETUP `a`, TEARDOWN TestB `a`, TEARDOWN `b`, TEARDOWN first `a`. `b` stays built from the first `a=4` (`8 != 6`). Same all versions.

Leftover `--collect-only test_override.py`: **2 collected** on 8.4.1–9.1.1. The miss is execute (`b` not rebuilt), not collect. No View staged.

Leftover `--setup-plan test_override.py`: 2 items, SETUP M `a` then SETUP M `b` (uses first `a`), then SETUP M `a` (class override) without rebuilding `b`, on 8.4.1–9.1.1. Same as execute. No tests ran. No View.

Leftover `--lf` after rebuild miss: seed **1 failed, 1 passed**; `--lf` **1 passed, 1 deselected** on 8.4.1–9.1.1. Rerunning only `TestB` skips the first module `a`, so `b` is rebuilt. `--lf` hides the override miss. No View.

Leftover `--ff`: miss **swaps onto TestA** (`assert 6 == 8`). Failed-first runs TestB first (now pass) then TestA fails. Miss still visible, swapped. No View.

Leftover `--nf`: still **TestB** `assert 8 == 6` (1 fail 1 pass). `--nf` does not hide or swap. No View.

Leftover `--sw`: first run interrupted 1 fail 1 pass; second **1 passed, 1 deselected**. `--sw` hides the override miss like `--lf`. No View.

Leftover `--maxfail=1`: still **1 failed, 1 passed** (TestB miss visible; TestA already passed). No View.
