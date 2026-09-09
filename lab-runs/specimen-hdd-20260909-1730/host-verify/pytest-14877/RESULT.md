# Host 実機 pytest#14877

Not Dreamer-facing. HOLD (profiler / feature). No View.

`get_config()` then `dir()` over `pluginmanager.get_plugins()`. Not a timed A/B. Not pytest's own suite.

| pytest | plugins | sum of `dir(plugin)` | `dir(TerminalReporter)` |
| --- | ---: | ---: | ---: |
| 8.4.1 | 32 | 1609 | 100 |
| 9.0.1 | 32 | 1670 | 102 |
| 9.0.3 | 32 | 1671 | 102 |
| 9.1.0 | 32 | 1700 | 103 |
| 9.1.1 | 32 | 1701 | 103 |

Reporter's 32-plugin count matches. Scan-size numbers are not the same as their cProfile table. No `__pytest_no_fixtures__` flag applied.

Leftover `get_config()` plugin count: **32** on 8.4.1–9.1.1. Same as the recorded table. No View/export.

Leftover `--setup-show count.py`: rc=5 no tests collected (not a `test_*.py`). Plugin-count leftover remains the `get_config()` script, not a pytest node. No View/export.
