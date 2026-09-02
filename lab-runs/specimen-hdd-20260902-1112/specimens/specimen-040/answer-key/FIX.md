KNOWN FIX (sealed): wntrblm/nox#393 merge 7ad30a0eedc6b6e477be34010153267bd5ff13f4.

The KeyboardInterrupt path called terminate, wait, then reraise every time, so a child that handled SIGINT and exited 0 still failed the Nox session (exit 130).

Repair: shutdown_process() tries communicate(timeout=0.3), then SIGTERM plus communicate(timeout=0.2), then SIGKILL plus communicate(); reraise KeyboardInterrupt only when proc.returncode != 0. A child that exits successfully after the interrupt is treated as handled.

Regression tests: test_interrupt_handled (child SystemExit on SIGINT, Nox does not raise) vs test_interrupt_raises (ignored SIGINT/SIGTERM, Nox still raises). Windows variants run in a secondary console session.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
