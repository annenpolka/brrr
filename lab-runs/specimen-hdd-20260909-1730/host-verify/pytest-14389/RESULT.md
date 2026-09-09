# Host 実機 pytest#14389

Not Dreamer-facing. HOLD for HDD consumer (no View/export). Did **not** implement `raise ... from exc`.

Public mini: `pytest.raises(ValueError, match="nope")` around `raise ValueError("actual")`.
- pytest 8.4.1 / 9.0.1 / 9.0.3: rc=1; report includes `During handling of the above exception, another exception occurred:` then `AssertionError: Regex pattern did not match`
- pytest 9.1.0 / 9.1.1: rc=1; `AssertionError: Regex pattern did not match` only (no "During handling")

Matches the reporter on 8.4/9.0. The connective is already gone from 9.1.0.

Leftover `--assert=plain`: 8.4.1 rc=1 **without** `During handling`. 9.0.1/9.0.3 still print `During handling`. 9.1.0/9.1.1 still omit it. `--assert=plain` removes the connective on 8.4.1 only.

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1. `During handling` is execute traceback, not collect. No View staged.

Leftover `--tb=line`: 8.4.1 one-line AssertionError (no `During handling`). 9.0.1/9.0.3 still print `During handling`. 9.1.0/9.1.1 omit it. Same 8.4.1 drop as `--assert=plain`; 9.1.0+ omit either way. No View staged.
