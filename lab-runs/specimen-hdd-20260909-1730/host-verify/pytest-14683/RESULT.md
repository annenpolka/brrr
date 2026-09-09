# Host 実機 pytest#14683

Not Dreamer-facing. HOLD for HDD consumer (no View/export).

Stripped public mini: session autouse injects `ANSWER=42` into `doctest_namespace`; `--doctest-modules mod.py`.
- pytest 8.4.1 / 9.0.1 / 9.0.3 / 9.1.0 / 9.1.1: rc=0, 1 passed

Does not reproduce the reporter (nimbus/xarray tree).

Leftover `--setup-show --doctest-modules`: **1 passed** on 8.4.1–9.1.1. `--setup-show` does not change the stripped mini. No View staged.

Leftover `--collect-only --doctest-modules`: **1 collected** (`mod.py::mod.foo`) on 8.4.1–9.1.1. No View staged.
