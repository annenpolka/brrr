# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Incremental compile with `-Znext-solver`. Same crate, two revisions, same incremental directory.

Revision cfail1:

```rust
pub trait Future {
    type Error;
    fn poll() -> Self::Error;
}

struct S;
impl Future for S {
    type Error = Error;
    fn poll() -> Self::Error { todo!() }
}

pub struct Error(());
```

Revision cfail2 changes only the struct shape:

```rust
pub struct Error();
```

`fn poll` still returns `Self::Error`, which normalizes to `Error`. The field of `Error` is gone.

The second session ICEs while decoding a DefId that no longer exists. The typeck query for `fn poll` was not marked red.

The developer wants to know which query identity the second session treated as still green, and which first-run dependency that identity did not record.

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

# COMMANDS

```
# test file is on the PR; not present on failing_ref
# compiletest incremental: cfail1 then cfail2, -Znext-solver
# ./x.py test tests/incremental/track-deps-in-new-solver.rs

# equivalent shape:
rustc track-deps-in-new-solver.rs --cfg cfail1 -Znext-solver -C incremental=incr --crate-type lib
rustc track-deps-in-new-solver.rs --cfg cfail2 -Znext-solver -C incremental=incr --crate-type lib
# second session: typeck of fn poll stays green; decode of removed Error field DefId
```

Not executed on this lab host.

rust-lang/rust
  compiler/rustc_query_system/src/dep_graph/graph.rs
  compiler/rustc_middle/src/ty/context.rs
  compiler/rustc_trait_selection/src/traits/select/mod.rs
  compiler/rustc_type_ir/src/search_graph/mod.rs
  tests/incremental/track-deps-in-new-solver.rs

RELEVANT MATERIAL

### in_task_old_solver.rs

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

### track-deps-in-new-solver.rs

//@ revisions: cfail1 cfail2
//@ compile-flags: -Znext-solver
//@ check-pass

pub trait Future {
    type Error;
    fn poll() -> Self::Error;
}

struct S;
impl Future for S {
    type Error = Error;
    fn poll() -> Self::Error {
        todo!()
    }
}

#[cfg(cfail1)]
pub struct Error(());

#[cfg(cfail2)]
pub struct Error();

fn main() {}

### with_anon_task_failing.rs

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

### with_cached_task_failing.rs

# Reduced excerpt of Interner for TyCtxt on failing_ref
# compiler/rustc_middle/src/ty/context.rs

fn with_cached_task<T>(self, task: impl FnOnce() -> T) -> (T, DepNodeIndex) {
    self.dep_graph.with_anon_task(self, crate::dep_graph::dep_kinds::TraitSelect, task)
}

### with_new_goal_cached_task.rs

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
