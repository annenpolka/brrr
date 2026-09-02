KNOWN FIX (sealed): rust-lang/rust PR 133828 merge 5a0a5e6db9727917ce3e36950dae92696bc17079.

`with_cached_task` built an anonymous TraitSelect DepNode and stored its index for later global-cache hits, but the parent query never recorded a read of that node on first evaluation. typeck(fn poll) therefore had no edge to type_of(Error). After Error dropped its field, type_of went red while typeck stayed green, and the reused typeck result decoded a vanished field DefId.

Repair: DepGraph::with_anon_task itself calls read_index on the produced node so first-run solver work is an edge of the caller. Query plumbing keeps an inner helper that does not read, because execute_job_incr records the anon node as the query itself. Old-solver in_task's explicit read becomes redundant and is removed.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
