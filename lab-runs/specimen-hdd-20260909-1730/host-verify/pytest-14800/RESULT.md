# Host 実機 pytest#14800

Not Dreamer-facing. HOLD no View.

Lazy `fixture:` param plus `pytest_fixture_setup` hook.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 2 passed, 1 skipped |
| 9.0.1 | 0 | 2 passed, 1 skipped |
| 9.0.3 | 0 | 2 passed, 1 skipped |
| 9.1.0 | 1 | 1 skipped, 2 errors (`assert not self._finalizers`) |
| 9.1.1 | 1 | same `_finalizers` AssertionError |

Leftover `--setup-show`: 8.4.1 / **9.0.1** / **9.0.3** teardown `skipping_base` then run `plain-1`/`plain-2` (2 passed, 1 skipped). **9.1.0 and 9.1.1** teardown `skipping_base` then `assert not self._finalizers`. Split is 9.1.0, not 9.0.1/9.0.3.

Leftover `--setup-plan`: no tests ran; the printed plan is the same on 8.4.1–9.1.1 (including 9.1.0/9.1.1). `_finalizers` fires on execute (`--setup-show`), not on plan.

Leftover `--tb=short` / `--assert=plain`: same split as run (8.4.1–9.0.3 2 passed 1 skipped; 9.1.0/9.1.1 1 skipped 2 errors `assert not self._finalizers`). Short/plain do not hide the pytest-internal AssertionError. No View/export.



Leftover `--collect-only`: **3 collected** on 8.4.1–9.1.1. `_finalizers` is execute, not collect. No View/export.

Leftover `--lf` after `_finalizers` (isolated cache): 8.4.1–9.0.3 seed 2 pass 1 skip; `--lf` reruns all (no last-failed). 9.1.0/9.1.1 seed 1 skip 2 errors; `--lf` reruns **2 failures then 2 passed** (skip not rerun, so `_finalizers` does not fire). `--lf` hides the `_finalizers` miss. No View/export.

Leftover `--ff` after `_finalizers` (isolated cache): 8.4.1–9.0.3 2 pass 1 skip. 9.1.0/9.1.1 seed 1 skip 2 errors; `--ff` **rerun previous 2 failures first** then **2 passed, 1 skipped**. Failed-first runs the plains before the skip, so `_finalizers` does not fire. `--ff` also hides the miss. No View/export.

Leftover `--maxfail=1`: 8.4.1–9.0.3 2 pass 1 skip. 9.1.0/9.1.1 **1 skipped, 1 error** (`plain-1` `_finalizers` only). `--maxfail=1` hides the second `_finalizers` error. No View/export.

Leftover `--nf` after `_finalizers` (isolated cache): 8.4.1–9.0.3 2 pass 1 skip. 9.1.0/9.1.1 **1 skipped, 2 errors** still. `--nf` does **not** hide `_finalizers` (unlike `--lf`/`--ff`/`--maxfail=1`). No View/export.

Leftover `--sw`: 8.4.1–9.0.3 2 pass 1 skip. 9.1.0/9.1.1 first run **interrupted** at `plain-1` `_finalizers` (1 skip 1 error). Second `--sw` **2 passed, 1 deselected** (skip already passed; plains run without skip first so `_finalizers` does not fire). `--sw` hides `_finalizers` like `--lf`/`--ff`/`--maxfail=1`. No View/export.
