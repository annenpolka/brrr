# Host 実機 pytest#14775

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public snippet is the class-scoped instance fixture under `-Werror`.
- pytest 8.4.1: rc=0, 2 passed
- pytest 9.0.1: rc=0, 2 passed
- pytest 9.0.3: rc=0, 2 passed
- pytest 9.1.0: rc=0, 2 passed, 1 warning
- pytest 9.1.1: rc=1, 2 errors (`PytestRemovedIn10Warning` then `AssertionError` on `_finalizers`)

Matches the reporter's 9.2.0.dev traceback shape.

Leftover `--setup-show` (no `-Werror`): 8.4.1–9.0.3 **2 passed**; 9.1.0/9.1.1 **2 passed, 1 warning** (`PytestRemovedIn10Warning`). No `_finalizers`.

Leftover `--setup-show -Werror`: 8.4.1–9.0.3 2 passed. 9.1.0 **and** 9.1.1 rc=1: test_1 warning-as-error, test_2 `AssertionError` (`_finalizers`). The `_finalizers` assert is the second-test consequence of the first class-fixture setup failing.

Leftover `--setup-plan -Werror`: no tests ran on 8.4.1–9.1.1 (same printed plan). Warning/`_finalizers` fire on execute, not on plan.

Leftover `-Werror` without `--setup-show`: 8.4.1–9.0.3 2 passed. **9.1.0 and 9.1.1** rc=1: test_1 warning-as-error, test_2 `_finalizers`. Holding `-Werror` constant, the `_finalizers` split is 9.1.0 (not 9.1.1-only). The original 9.1.0 "2 pass 1 warning" run did not convert the warning.

Leftover `--tb=short` (no `-Werror`): 8.4.1–9.0.3 2 passed; 9.1.0/9.1.1 2 passed 1 warning. Leftover `--tb=short -Werror`: 8.4.1–9.0.3 2 passed; 9.1.0/9.1.1 2 errors (`PytestRemovedIn10Warning` then `AssertionError`). Short traceback does not hide either error. No View staged.

Leftover `--collect-only`: **2 collected** on 8.4.1–9.1.1. `_finalizers` is execute, not collect. No View staged.

Leftover `--lf -Werror` after class-fixture warning: 8.4.1–9.0.3 seed 2 pass; `--lf` 2 pass. 9.1.0/9.1.1 seed 2 errors (warning-as-error then `_finalizers`); `--lf` reruns **both still 2 errors**. `--lf` does not hide this miss. No View staged.

Leftover `--ff -Werror`: 8.4.1–9.0.3 2 pass. 9.1.0/9.1.1 `--ff` reruns both errors first, still **2 errors**. `--ff` does not hide this miss. No View staged.

Leftover `--maxfail=1 -Werror`: 8.4.1–9.0.3 2 pass. 9.1.0/9.1.1 **1 error** (test_1 warning-as-error only). `--maxfail=1` hides the second-test `_finalizers`. No View staged.

Leftover `--nf -Werror` (isolated cache, `-Werror` on both runs): 8.4.1–9.0.3 2 pass. 9.1.0/9.1.1 seed 2 errors; `--nf` still **2 errors**. `--nf` does **not** hide `_finalizers` (same as #14800 `--nf`; unlike `--lf`/`--ff`/`--maxfail=1`). No View staged.

Leftover `--sw -Werror`: 8.4.1–9.0.3 2 pass. 9.1.0/9.1.1 first run interrupted at test_1 warning-as-error; second `--sw` still **1 error** on test_1 (0 already passed). `--sw` hides the second-test `_finalizers`. No View staged.
