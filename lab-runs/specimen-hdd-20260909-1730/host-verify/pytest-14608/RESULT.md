# Host 実機 pytest#14608

Not Dreamer-facing. HOLD no View.

Sibling `A/` + `B/` with `pytest_addoption("--from-b")` only in `B/conftest.py`.

| pytest | command | rc | result |
| --- | --- | --- | --- |
| 8.4.1 | `pytest --from-b A` | 4 | unrecognized arguments `--from-b` |
| 9.0.1 | `pytest --from-b A` | 4 | same |
| 9.0.3 | `pytest --from-b A` | 4 | same |
| 9.1.0 | `pytest --from-b A` | 4 | same |
| 9.1.1 | `pytest --from-b A` | 4 | same |
| 8.4.1 | `pytest --from-b A B` | 0 | 2 passed |
| 9.0.1 | `pytest --from-b A B` | 0 | 2 passed |
| 9.0.3 | `pytest --from-b A B` | 0 | 2 passed |
| 9.1.0 | `pytest --from-b A B` | 0 | 2 passed |
| 9.1.1 | `pytest --from-b A B` | 0 | 2 passed |
| 8.4.1 | cwd=`A` `pytest --from-b ../B` | 0 | 1 passed |
| 9.0.1 | cwd=`A` `pytest --from-b ../B` | 0 | 1 passed |
| 9.0.3 | cwd=`A` `pytest --from-b ../B` | 0 | 1 passed |
| 9.1.0 | cwd=`A` `pytest --from-b ../B` | 0 | 1 passed |
| 9.1.1 | cwd=`A` `pytest --from-b ../B` | 0 | 1 passed |

No 8.x vs 9.x delta in this sibling `A/`+`B/` sketch. The 9.1.0-only miss is the invocation-dir `tests/` layout in `pytest-14608c`.

Leftover `--collect-only --from-b A`: rc=4 unrecognized on 8.4.1–9.1.1. Leftover `--collect-only --from-b A B`: **2 collected** all versions. Same as run.

Leftover `--setup-show --from-b A B`: **2 passed** on 8.4.1–9.1.1. No 8/9 delta. No View/export.
