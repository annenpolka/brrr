KNOWN FIX (sealed): pytest-dev/pytest-xdist PR 1324 merge 63f908d5ebc041654475597c3f2d6f1ee3da2c8f.

remove_node requeued the whole assigned workload, including scopes whose tests were already True. The replacement then received send_runtest_some([]) and hung. Repair: requeue a scope only if any(not completed); _assign_work_unit raises RuntimeError if a unit has no pending indexes.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
