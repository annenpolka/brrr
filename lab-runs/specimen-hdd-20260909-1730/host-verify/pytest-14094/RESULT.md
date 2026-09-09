# Host 実機 pytest#14094

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Public snippet as written uses `pytest.Monkeypatch.context()`.
- pytest 8.4.1: rc=1 same `Monkeypatch` AttributeError
- pytest 9.0.1: rc=1 `AttributeError: module 'pytest' has no attribute 'Monkeypatch'`
- pytest 9.0.3: rc=1 same `Monkeypatch` AttributeError
- pytest 9.1.0: rc=1 same `Monkeypatch` AttributeError
- pytest 9.1.1: rc=1 same

Snippet is not a runnable public API. No View staged. Host did not pass a repaired `MonkeyPatch` spelling to a Dreamer.

Leftover `--tb=short`: still `AttributeError: module 'pytest' has no attribute 'Monkeypatch'` on 8.4.1–9.1.1. Traceback style does not change the misspelling.

Leftover `--collect-only test_delitem.py`: **2 collected** on 8.4.1–9.1.1. `Monkeypatch` AttributeError is execute, not collect. No View.

Leftover `--lf`/`--ff`/`--nf`: still **2 failed** `Monkeypatch` AttributeError on 8.4.1–9.1.1. Leftover `--sw`: 1 failed interrupted (hides the later miss). No View.

Leftover `--maxfail=1`: seed 2 failed then `--maxfail=1` **1 failed** (hides the later miss). No View.
