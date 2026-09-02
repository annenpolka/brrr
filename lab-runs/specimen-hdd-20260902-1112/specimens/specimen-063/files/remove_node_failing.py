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
