# Host 実機 pytest#13784

Not Dreamer-facing. HOLD no View.

`pytest -svv` with `capteesys`. Count of `Hello world stdout` in captured session output.

| pytest | rc | stdout copies |
| --- | --- | --- |
| 8.4.1 | 0 | 2 (doubled) |
| 9.0.1 | 0 | 2 (doubled) |
| 9.0.3 | 0 | 2 (doubled) |
| 9.1.0 | 0 | 1 |
| 9.1.1 | 0 | 1 |
| 8.4.1 `-s` without `capteesys` | 0 | 1 |
| 9.1.1 `-s` without `capteesys` | 0 | 1 |

Doubling is 8.4.1 `capteesys` + `-s`. Tests pass.

Leftover `--setup-show -svv test.py`: same split (8.4.1–9.0.3 **2** stdout copies; 9.1.0/9.1.1 **1**). SETUP/TEARDOWN `capteesys` on all versions. `--setup-show` does not change the doubling.

Leftover `--collect-only test.py`: **1 collected** on 8.4.1–9.1.1. Doubling is execute (`-s` + capteesys), not collect. No View/export.

Leftover `--tb=short -s test.py`: stdout still doubled through 9.0.3 (`Hello world stdout` twice), once from 9.1.0. `--tb=short` does not change capteesys doubling. No View.

Leftover `--assert=plain -s test.py`: stdout still doubled through 9.0.3, once from 9.1.0. `--assert=plain` does not change capteesys doubling. No View.

Leftover `--tb=line -s test.py`: stdout still doubled through 9.0.3 (`Hello world stdout` twice), once from 9.1.0. `--tb=line` does not change capteesys doubling. No View.
