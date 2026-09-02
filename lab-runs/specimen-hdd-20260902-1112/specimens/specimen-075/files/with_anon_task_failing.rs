# Reduced excerpt of DepGraph::with_anon_task on failing_ref
# compiler/rustc_query_system/src/dep_graph/graph.rs

pub fn with_anon_task<Tcx: DepContext<Deps = D>, OP, R>(
    &self,
    cx: Tcx,
    dep_kind: DepKind,
    op: OP,
) -> (R, DepNodeIndex)
where
    OP: FnOnce() -> R,
{
    match self.data() {
        Some(data) => data.with_anon_task(cx, dep_kind, op),
        None => (op(), self.next_virtual_depnode_index()),
    }
}
