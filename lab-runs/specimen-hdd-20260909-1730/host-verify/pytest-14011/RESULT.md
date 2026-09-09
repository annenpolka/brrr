# Host 実機 pytest#14011

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

pytest 9.0.1: 2 failed. `self.variable` is None on the test instance after a class-scoped fixture on a base class ran `setup` on a different instance. Matches the reporter's "both tests fail".
- pytest 9.1.1: rc=1 (host refute; still HOLD, no View)
- pytest 8.4.1: rc=1 (host refute; still HOLD, no View)
