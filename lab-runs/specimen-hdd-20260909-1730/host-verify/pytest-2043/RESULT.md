# Host 実機 pytest#2043

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public mixin + indirect parametrize snippet (pytest 3 era).
- pytest 8.4.1: rc=2 collection `function uses no fixture 'a'`
- pytest 9.0.1: rc=0, 4 passed
- pytest 9.0.3: rc=0, 4 passed
- pytest 9.1.0: rc=2 `duplicate parametrization of 'a'`
- pytest 9.1.1: rc=0, 4 passed

9.1.0 vs 9.1.1 matches the 14591 family.

Leftover `--collect-only`: 8.4.1 rc=2 `function uses no fixture 'a'` (TestOverriden). 9.0.1/9.0.3/9.1.1 4 tests collected. 9.1.0 rc=2 `duplicate parametrization of 'a'` on both TestNormal and TestOverriden. Same split as run.

Leftover `--setup-show`: same split (8.4.1 no-fixture collect error; 9.1.0 duplicate on both classes; 9.0.1/9.0.3/9.1.1 4 passed).

Leftover `--tb=short`: same split (8.4.1 `function uses no fixture 'a'`; 9.1.0 duplicate on both classes; 9.0.1/9.0.3/9.1.1 4 passed). `--tb=short` does not change collect errors. No View staged.

Leftover `--setup-plan test_ab.py`: 8.4.1 rc=2 collect `function uses no fixture 'a'`. 9.0.1/9.0.3/9.1.1 4 items. **9.1.0** collect ERROR `duplicate parametrization of 'a'`. Same split as run. No View.

Leftover `--lf` `test_ab.py`: 8.4.1 collect `function uses no fixture 'a'`; `--lf` still that collect error. **9.1.0** duplicate collect; `--lf` still. 9.1.1 4 pass; `--lf` no last-failed. Collect-error is not last-failed. No View.

Leftover `--ff` `test_ab.py`: 8.4.1 collect no-fixture; `--ff` still. **9.1.0** duplicate collect; `--ff` still. 9.1.1 4 pass; `--ff` no last-failed. Collect-error is not last-failed. No View.
