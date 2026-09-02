# Reduced excerpt of Interner for TyCtxt on failing_ref
# compiler/rustc_middle/src/ty/context.rs

fn with_cached_task<T>(self, task: impl FnOnce() -> T) -> (T, DepNodeIndex) {
    self.dep_graph.with_anon_task(self, crate::dep_graph::dep_kinds::TraitSelect, task)
}
