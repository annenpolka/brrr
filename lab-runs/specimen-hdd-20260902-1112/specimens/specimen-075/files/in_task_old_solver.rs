# Reduced excerpt of SelectionContext::in_task on failing_ref
# compiler/rustc_trait_selection/src/traits/select/mod.rs

fn in_task<OP, R>(&mut self, op: OP) -> (R, DepNodeIndex)
where
    OP: FnOnce(&mut Self) -> R,
{
    let (result, dep_node) =
        self.tcx().dep_graph.with_anon_task(self.tcx(), dep_kinds::TraitSelect, || op(self));
    self.tcx().dep_graph.read_index(dep_node);
    (result, dep_node)
}
