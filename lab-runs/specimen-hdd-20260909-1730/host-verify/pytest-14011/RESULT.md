# Host 実機 pytest#14011

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

pytest 9.0.1: 2 failed. `self.variable` is None on the test instance after a class-scoped fixture on a base class ran `setup` on a different instance. Matches the reporter's "both tests fail".
- pytest 9.0.3: rc=1 both tests fail
- pytest 9.1.0: rc=1 both tests fail (`None == 'test1'/'test2'`)
- pytest 9.1.1: rc=1 (host refute; still HOLD, no View)
- pytest 8.4.1: rc=1 (host refute; still HOLD, no View)

Leftover `--setup-show`: SETUP/TEARDOWN class `fix` **once per subclass** on 8.4.1–9.1.1. Both tests still fail (`self.variable` is None on the test instance). 9.1.0/9.1.1 also emit 2 `PytestRemovedIn10Warning` (class-scoped fixture as instance method). The class fixture runs; attributes set on the fixture instance do not appear on the test instance.

Leftover `--collect-only test_inherit.py`: **2 collected** on 8.4.1–9.1.1. The miss is execute (`self.variable` None), not collect. Leftover `--tb=short`: both tests still `assert None == 'test1'/'test2'` on 8.4.1–9.1.1; 9.1.0/9.1.1 also 2 warnings. No View.

Leftover `--setup-plan test_inherit.py`: SETUP C `fix` per subclass, 2 collected, on 8.4.1–9.1.1. `self.variable` None is execute, not plan. No View.

Leftover `--lf` / `--ff`: still **2 failed** `self.variable is None` on 8.4.1–9.1.1. Last-failed rerun does not attach the class fixture attribute. No View.
