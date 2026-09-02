# OBSERVED

Public rust-lang/rust PR 133828. Failing world in `compiler/rustc_query_system/src/dep_graph/graph.rs`, `compiler/rustc_middle/src/ty/context.rs`, and `compiler/rustc_type_ir/src/search_graph/mod.rs` around merge parent `acabb5248231987ae1f0c215208d1005a5db402d`.

New-solver goal evaluation wraps work in `with_cached_task` and later stores the returned index:

```
let ((final_entry, result), dep_node) = cx.with_cached_task(|| {
    self.evaluate_goal_in_task(cx, input, inspect, &mut evaluate_goal)
});
// ...
self.insert_global_cache(cx, input, final_entry, result, dep_node)
```

On this revision, `TyCtxt`'s Interner impl is:

```
fn with_cached_task<T>(self, task: impl FnOnce() -> T) -> (T, DepNodeIndex) {
    self.dep_graph.with_anon_task(self, crate::dep_graph::dep_kinds::TraitSelect, task)
}
```

`DepGraph::with_anon_task` forwards and returns `(result, dep_node_index)` with no `read_index` of that index:

```
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
```

The old solver's `SelectionContext::in_task` on the same revision does call `read_index`:

```
let (result, dep_node) =
    self.tcx().dep_graph.with_anon_task(self.tcx(), dep_kinds::TraitSelect, || op(self));
self.tcx().dep_graph.read_index(dep_node);
(result, dep_node)
```

A PR description of this revision: first-run new-solver goals did not record the queries they called. Incremental typeck of `fn poll` stayed green after `Error` lost its field. `type_of` for `Error` is red (`ty::Adt` carries `AdtDef`, whose stable hash changes with the field). Normalizing `Self::Error` into `Error` should have read that `type_of`. The green typeck result then tried to decode the removed field's DefId.

Demonstration source (added on the PR, not on the merge parent):

```
//@ revisions: cfail1 cfail2
//@ compile-flags: -Znext-solver
//@ check-pass
```

This packet does not include a local clone; treat the snippets and incremental split as the world. Do not execute untrusted checkouts on the host.
