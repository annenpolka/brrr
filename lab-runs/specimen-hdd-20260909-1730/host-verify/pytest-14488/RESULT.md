# Host 実機 pytest#14488

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public claim: `caplog.handler` after the stash key is gone raises an opaque `KeyError` with a `StashKey` address, not `RuntimeError`.

| pytest | `caplog.handler` present | after `del stash[caplog_handler_key]` |
| --- | --- | --- |
| 8.4.1 | pass | rc=1 `KeyError: <_pytest.stash.StashKey object at ...>` |
| 9.0.1 | pass | same KeyError |
| 9.0.3 | pass | same KeyError |
| 9.1.0 | pass | same KeyError |
| 9.1.1 | pass | same KeyError |

No 8/9 delta. Happy `caplog` still works (see also #14436). Tavern tree not cloned.

Leftover `--tb=short`: still 1 failed / 1 passed `KeyError: <StashKey>` on 8.4.1–9.1.1.

Leftover `--collect-only test_handler.py`: **2 collected** on 8.4.1–9.1.1. StashKey KeyError is execute, not collect. No View/export. PR stays 正解 off Dreamer.

Leftover `--nf`: still 1 failed 1 passed `StashKey`. Leftover `--sw`: first 1 failed 1 passed interrupted; second 1 failed 1 deselected. Leftover `--maxfail=1`: still 1 failed 1 passed (fail is first). No View.
