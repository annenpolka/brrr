# Host 実機 pytest#13885

Not Dreamer-facing. HOLD for consumer (no View).

pytest 8.4.1 rc=1; pytest 9.0.1 rc=1; pytest 9.0.3 rc=1. Autouse fixture vs unittest skipIf.
- pytest 9.1.0: rc=0 1 skipped (same as 9.1.1)
- pytest 9.1.1: rc=0 (host refute; still HOLD, no View)

Leftover `--setup-show`: 8.4.1/9.0.3 SETUP autouse `something` then ERROR `assert 0` (skipIf does not skip autouse). 9.1.0/9.1.1 SETUP `_unittest_skip_fixture_Foo` then 1 skipped (autouse never fires). Split is 9.1.0.

Leftover `--setup-plan`: no tests ran on 8.4.1–9.1.1. 8.4.1–9.0.3 print SETUP/TEARDOWN autouse `something`. 9.1.0/9.1.1 print SETUP `_unittest_skip_fixture_Foo` **and** SETUP/TEARDOWN `something`. Plan still lists the autouse on 9.1.0 even though `--setup-show` execute never fires it.

Leftover `--tb=short`: same split as run (8.4.1–9.0.3 ERROR `assert 0` in autouse `something`; 9.1.0/9.1.1 1 skipped). `--tb=short` does not change skip vs fire.

Leftover `--collect-only test_skip.py`: **1 collected** on 8.4.1–9.1.1 including 9.1.0. Skip vs autouse fire is execute, not collect. No View.

Leftover `--lf` after skipIf+autouse (isolated cache): 8.4.1–9.0.3 seed ERROR `assert 0`; `--lf` reruns the error still ERROR. 9.1.0/9.1.1 seed **1 skipped**; `--lf` no last-failed, 1 skipped. `--lf` does not hide the 8/9 skip-vs-fire split. No View.

Leftover `--ff` after skipIf+autouse: 8.4.1–9.0.3 still ERROR `assert 0`; 9.1.0/9.1.1 1 skipped (no last-failed). `--ff` does not hide the 8/9 split. No View.

Leftover `--maxfail=1`: 8.4.1–9.0.3 still ERROR `assert 0`; 9.1.0/9.1.1 1 skipped. `--maxfail=1` does not change the skip-vs-fire split (only one test). No View.

Leftover `--nf`: 8.4.1–9.0.3 still ERROR `assert 0`; 9.1.0/9.1.1 1 skipped. `--nf` does not change the skip-vs-fire split. No View.

Leftover `--sw`: 8.4.1–9.0.3 first run interrupted 1 error; second `--sw` still 1 error. 9.1.0/9.1.1 both runs **1 skipped** (no previously failed tests). `--sw` does not hide the 8/9 skip-vs-fire split. No View.
