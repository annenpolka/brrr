CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public pytest-dev/pytest-xdist#1323 / PR 1324. LoadScopeScheduling (`src/xdist/scheduler/loadscope.py`) is shared by `--dist=loadscope` and `--dist=loadgroup`.

Reporter file:

```
def test_1():
    assert True

def test_2():
    import time
    time.sleep(5)
    assert True
```

On the failing revision, `remove_node` after a crash does:

```
# Made uncompleted work unit available again
self.workqueue.update(workload)
```

`workload` is the crashed node's entire assigned dict: scope → {nodeid: completed_bool}. `update` puts *every* scope back, including scopes whose tests are already True.

Later `_assign_work_unit` pops a scope and builds:

```
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)
```

If the requeued unit has only completed items, `nodeids_indexes` is empty. `send_runtest_some([])` leaves the replacement worker waiting. Remote side hangs in `xdist/remote.py` around the runtest-some receive.

A PR acceptance case uses `os._exit(1)` in `test_b` after `test_a` passed, `-n1 --dist=loadgroup`. On the failing revision that suite never finishes.

This packet does not include a local clone; treat the snippets and hang as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
pytest -n1 --dist=loadgroup testing/test_timeout.py
# PR acceptance name:
#   test_loadgroup_does_not_hang_after_restart
```

Not executed on this lab host.

pytest-dev/pytest-xdist
  src/xdist/scheduler/loadscope.py
  src/xdist/remote.py
  testing/acceptance_test.py

RELEVANT MATERIAL

### hang_log.txt

replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
# suite never finishes under --dist=loadgroup

### remove_node_failing.py

# Reduced excerpt of LoadScopeScheduling on failing_ref
# src/xdist/scheduler/loadscope.py

# inside remove_node, after identifying crashitem:
# Made uncompleted work unit available again
self.workqueue.update(workload)

# inside _assign_work_unit:
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
