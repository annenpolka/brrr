# Host 実機 pytest#14436

Not Dreamer-facing. HOLD for HDD consumer (no View/export). Not the tavern tree.

- happy `caplog.at_level`: pytest 8.4.1/9.0.1/9.0.3/9.1.0/9.1.1 rc=0
- session-scoped wrapper around `caplog`: ScopeMismatch, not KeyError (8.4.1/9.0.1/9.0.3/9.1.0/9.1.1)
- `-p no:logging`: fixture `caplog` not found, not KeyError (8.4.1/9.0.1/9.0.3/9.1.0/9.1.1)

Reporter's stash KeyError needs the tavern skip test. No View staged.

Leftover `--tb=short` of the parent tree hits leftover layout name collisions (`session_fix/test_cap.py`). Per-layout happy/ScopeMismatch/no:logging results already recorded. No View.

Leftover isolated `happy/`/`nolog/` `--lf`/`--ff`/`--sw`: **1 passed** on 8.4.1–9.1.1. Leftover `session_fix/` `--lf`/`--sw`: still **1 error** ScopeMismatch (not last-failed hide of a later test; the only test errors). No View.

Leftover `session_fix/` `--ff`/`--nf`/`--maxfail=1`: still **1 error** ScopeMismatch on 8.4.1–9.1.1. No View.
