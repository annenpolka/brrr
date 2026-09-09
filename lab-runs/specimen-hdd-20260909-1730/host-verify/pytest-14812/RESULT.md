# Host 実機 pytest#14812

Not Dreamer-facing. HOLD no View. Do not apply the PR.

`pytest_runtest_makereport` wrapper reads `item.funcargs["caplog"].text` on teardown.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 3 | INTERNALERROR `KeyError: StashKey` in `caplog.handler`; test itself 1 passed |
| 9.0.1 | 3 | same |
| 9.0.3 | 3 | same |
| 9.1.0 | 3 | same |
| 9.1.1 | 3 | same |

Same stash KeyError family as #14488, but the access is during teardown report creation.

Leftover `--tb=short`: still INTERNALERROR `KeyError: StashKey` on 8.4.1–9.1.1. Traceback style does not avoid the stash access.

Leftover `--setup-show`: still INTERNALERROR StashKey `caplog.handler` on 8.4.1–9.1.1 (1 passed then INTERNALERROR). `--setup-show` does not skip teardown makereport. No View/export.

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1. INTERNALERROR StashKey is execute, not collect. No View/export.

Leftover `--assert=plain`: still INTERNALERROR StashKey `caplog.handler` on 8.4.1–9.1.1 (1 passed then INTERNALERROR). Plain assert does not skip teardown makereport. No View/export.
