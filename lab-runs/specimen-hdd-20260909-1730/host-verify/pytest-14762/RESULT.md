# Host 実機 pytest#14762

Not Dreamer-facing. HOLD no View. No render-engine clone.

Reporter: SEGFAULT during collection on CPython **3.15b4** + pytest 9.1.1 (Ubuntu CI).

This host: CPython **3.14.5**. `pytest --collect-only test_collect.py` on 9.1.1 rc=0, 1 collected. No segfault.

Cannot reproduce a 3.15b4 crash here.

Leftover `--collect-only --setup-show`: **1 collected** on 8.4.1–9.1.1. No segfault on this 3.14.5 host. No View/export.

Leftover `--setup-show`: **1 passed** on 8.4.1–9.1.1. No segfault on this 3.14.5 host. No View/export.

Leftover `--tb=short`: **1 passed** on 8.4.1–9.1.1. No segfault. No View/export.
