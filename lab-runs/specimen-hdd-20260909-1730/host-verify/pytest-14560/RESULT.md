# Host 実機 pytest#14560

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Issue had only a traceback. Host used a dict-wrapper with `__getattr__` returning `self[name]` (KeyError).
- pytest 8.4.1 / 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1: rc=2 collection `KeyError: '__name__'`
- plain `dict` parametrize is not in the failing collect path

Not the reporter's original file. No View staged.

Leftover `--tb=short`: still rc=2 collection `KeyError: '__name__'` on 8.4.1–9.1.1. Traceback style does not change collect.

Leftover `--collect-only test_box.py`: same rc=2 `KeyError: '__name__'` on 8.4.1–9.1.1. Collect-only still hits it. No View.

Leftover `--nf`/`--maxfail=1`: still rc=2 collect-error `KeyError: '__name__'` on 8.4.1–9.1.1. Collect-error is not last-failed. No View.
