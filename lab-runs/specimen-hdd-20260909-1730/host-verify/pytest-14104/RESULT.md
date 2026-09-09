# Host 実機 pytest#14104 comment session-fixture gap

Not Dreamer-facing. HOLD no View. PR not applied.

Public comment mini: session `foo` with `parametrize(..., indirect=True)` on `test_a`/`test_c` and a gap `test_b`.

| pytest | `test_b` is `pass` | `test_b` calls `getfixturevalue("foo")` |
| --- | --- | --- |
| 8.4.1 | rc=0 3 passed | rc=0 3 passed |
| 9.0.1 | rc=0 3 passed | rc=0 3 passed |
| 9.0.3 | rc=0 3 passed | rc=0 3 passed |
| 9.1.0 | rc=0 3 passed | rc=0 3 passed |
| 9.1.1 | rc=0 3 passed | rc=0 3 passed |

`--setup-show` leftover: session `foo[1]` is set up once, `test_b` runs in the middle, teardown is at the end (8.4.1/9.0.1/9.0.3/9.1.0/9.1.1). Host **carries** the session fixture across the gap (not option 1 "teardown after test_a"). `getfixturevalue("foo")` on `test_b` then does TEARDOWN `foo[1]` and SETUP unparametrized `foo` (8.4.1 and 9.1.1). Still 3 passed.

Leftover directory collect (both `test_gap.py` and `test_get.py`): **6 passed** on 8.4.1–9.1.1. Session carry is not an interleaved-gap miss. No View/export.


Leftover `--setup-plan test_gap.py`: SETUP S `foo[1]` once, used by `test_a`/`test_c` with `test_b` in between, TEARDOWN at end, on 8.4.1–9.1.1. Session carry is visible at plan. Leftover `--setup-plan` directory: 6 collected, two SETUP S `foo[1]`, same all versions. No View/export.
