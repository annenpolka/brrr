# Reduced excerpt of SearchGraph::with_new_goal on failing_ref
# compiler/rustc_type_ir/src/search_graph/mod.rs

// This is for global caching, so we properly track query dependencies.
// Everything that affects the `result` should be performed within this
// `with_anon_task` closure. If computing this goal depends on something
// not tracked by the cache key and from outside of this anon task, it
// must not be added to the global cache. Notably, this is the case for
// trait solver cycles participants.
let ((final_entry, result), dep_node) = cx.with_cached_task(|| {
    self.evaluate_goal_in_task(cx, input, inspect, &mut evaluate_goal)
});
// ...
self.insert_global_cache(cx, input, final_entry, result, dep_node)
