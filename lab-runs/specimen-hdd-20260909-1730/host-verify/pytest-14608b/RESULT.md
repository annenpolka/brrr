# Host 実機 pytest#14608 extra layouts

Not Dreamer-facing. HOLD no View. PR #14622/#14624 not applied.

Reporter sketch: invoke from directory `A` while `B/conftest.py` registers `--from-b`.

| layout | pytest | rc | result |
| --- | --- | --- | --- |
| `cd A && pytest --from-b` (no path) | 8.4.1–9.1.1 | 4 | unrecognized `--from-b` |
| parent `pytest.ini` `testpaths = A B`; `cd A && pytest --from-b` | 8.4.1/9.0.1/9.1.0/9.1.1 | 4 | unrecognized `--from-b` (inifile seen; B conftest not initial) |
| parent `pytest.ini`; from ini root `pytest --from-b` | 8.4.1/9.0.1/9.1.0/9.1.1 | 0 | 2 passed |

No 8.x vs 9.1.0 delta in these layouts. Nested `ini/` copies in the same tree made `pytest --from-b ..` collect duplicate addoption (ValueError) on every version; that is not the reporter split.

Leftover `--collect-only --from-b` of the parent tree hits leftover nested `ini/` copies (`ValueError` duplicate addoption / name collisions). Per-layout results already recorded. No View/export.
