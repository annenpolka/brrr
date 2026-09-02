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
