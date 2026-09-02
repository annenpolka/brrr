# TASK

pytest-xdist with `--dist=loadgroup` hangs after a worker is replaced. Other distribution modes finish.

A two-test file, one worker, faulthandler killing the worker mid-run:

```
pytest -n1 --dist=loadgroup -o faulthandler_timeout=1 -o faulthandler_exit_on_timeout=true testing/test_timeout.py
```

Observed log, then stall:

```
replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
```

The developer wants to know which work units were put back on the queue after the crash, which of those units were already completed, and why the replacement worker never finishes.
