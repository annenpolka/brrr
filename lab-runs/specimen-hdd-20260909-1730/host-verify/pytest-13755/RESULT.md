# Host 実機 pytest#13755

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public snippet `test_heavy.py` (session-scoped indirect `heavy_fixture` + mixed parametrize).
`--log-cli-level=INFO` fixture-call cache:

| pytest | rc | unique params | total setups |
| --- | --- | --- | --- |
| 8.4.1 | 0 | 4 | 10 (`FIRST !ZZZ!` 3, `FIRST !XXX!` 3, `SECOND` 2+2) |
| 9.0.1 | 0 | 4 | 10 same |
| 9.0.3 | 0 | 4 | 10 same |
| 9.1.0 | 0 | 4 | 10 same |
| 9.1.1 | 0 | 4 | 10 same |

Matches the reporter's re-init counts. Same on 8.4 and 9.x; not a 9-only delta.

Leftover `--setup-show` on 8.4.1 and 9.1.1: session `heavy_fixture` is torn down between param groups (e.g. `('FIRST','!ZZZ!')` then `('FIRST','!XXX!')`). Same 8/9. Leftover 9.0.1/9.0.3/9.1.0: **10 SETUP S / 10 TEARDOWN S** `heavy_fixture` (same as 8.4.1/9.1.1). The further-minimized `pytest-13755b` shows the same-param re-setup ERROR.

Leftover `--collect-only test_heavy.py`: **22 collected** on 8.4.1–9.1.1. The 10 setups are execute, not collect. No View staged.

Leftover `--setup-plan test_heavy.py`: **22 collected**, **10 SETUP S / 10 TEARDOWN S** `heavy_fixture` on 8.4.1–9.1.1 including 9.1.0. Plan matches execute. No tests ran. No View staged.
