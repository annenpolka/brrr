# Host 実機 pytest#14004

Not Dreamer-facing. HOLD no View.

Nested autouse conftest.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 4 passed |
| 9.0.1 | 0 | 4 passed |
| 9.0.3 | 0 | 4 passed |
| 9.1.0 | 0 | 4 passed |
| 9.1.1 | 0 | 4 passed |

Does not reproduce a sibling testpaths leak as a failing mini.

Leftover `--setup-show`: 4 passed on 8.4.1–9.1.1; SETUP `inner_fixture` once + `outer_fixture` four times. Same as run. The leak lives in `pytest-14004b` (`sdk/` + testpaths).

Leftover `--collect-only tests/sdk`: **4 collected** on 8.4.1–9.1.1. No leak at collect. No View/export.

Leftover `--setup-plan` from the tests mini: **4 collected** on 8.4.1–9.1.1. No inner autouse leak at plan (leak lives in pytest-14004b `sdk/` + testpaths). No tests ran. No View.
