# Host 実機 pytest#14271 comment monkeypatch undo

Not Dreamer-facing. HOLD no View. Do not apply PR #14271.

Public comment mini: `delattr(..., raising=False)` then `obj.attr = 42` inside `monkeypatch.context()`; after the context, `hasattr(obj, "attr")`.

| pytest | rc | result |
| --- | --- | --- |
| 8.4.1 | 0 | 1 passed (`hasattr` True) |
| 9.0.1 | 0 | 1 passed |
| 9.0.3 | 0 | 1 passed |
| 9.1.0 | 0 | 1 passed |
| 9.1.1 | 0 | 1 passed |

Host matches the commenter's current-behavior expectation (monkeypatch does not undo a later setattr). The PR's undo-missing-attr change is not applied. No 8/9 delta.

Leftover `delitem(..., raising=False)` then `d["k"] = 42`: `"k" in d` True on 8.4.1–9.1.1 (1 passed). No View/export.

Leftover `--setup-show test_delitem.py`: **1 passed**, SETUP F `monkeypatch`, on 8.4.1–9.1.1. No View/export.

Leftover `--setup-show test_mp.py`: **1 passed** on 8.4.1–9.1.1. No View/export.
