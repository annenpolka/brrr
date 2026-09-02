# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Incremental Compilation ICE

**Environment State**: Rust compiler (rustc) with `-Znext-solver` enabled, incremental compilation directory (`incr`), two revisions of a crate (cfail1 and cfail2). Observed ICE during second compilation due to missing DefId.

**Objective**: Identify which query was incorrectly marked green and which dependency was missing from its recorded dependencies.

**Commands Executed**:

1. **Initial Compilation (cfail1)**:
```bash
rustc track-deps-in-new-solver.rs --cfg cfail1 -Znext-solver -C incremental=incr --crate-type lib -Zdump-dep-graph
```
**Output**:  
Successful compilation. Dep graph written to `incr/dep-graph.bin`.  
**Observation**:  
Dep graph contains `typeck_of` node for `S::poll` and `type_of` node for `Error`.

2. **Dep Graph Inspection (cfail1)**:
```bash
rustc -Zquery-dep-graph "typeck_of(DefId(2:5))" --incremental incr
```
**Output**:  
```
Dependencies for typeck_of(DefId(2:5)):
- trait_def(DefId(2:4))
- adt_def(DefId(2:3))  
```
**Observation**:  
No edge to `type_of(DefId(2:10))` (the `Error` type) recorded. Normalization of `Self::Error` → `Error` not captured in dependencies.

3. **Second Compilation (cfail2)**:
```bash
rustc track-deps-in-new-solver.rs --cfg cfail2 -Znext-solver -C incremental=incr --crate-type lib -Zincremental-info
```
**Output**:  
```
ICE: def_id 2:11 not found in crate metadata (was field in Error(()) struct)
Reused queries:
- typeck_of(DefId(2:5)) [green]
```
**Failure**:  
ICE occurs during decoding of removed field (DefId 2:11).  
**Observation**:  
`typeck_of` for `S::poll` incorrectly marked green despite `type_of(Error)` changing.

4. **Query Verification**:
```bash
rustc -Zquery-dep-graph "type_of(DefId(2:10))" --incremental incr
```
**Output**:  
```
type_of(DefId(2:10)) changed since last compilation:
- Hash cfail1: 7d3f...a21c
- Hash cfail2: 9e0b...4fd1
```

**Key Findings**:  
1. **Incorrectly Green Query**:  
   `typeck_of(DefId(2:5))` (type-checking of `S::poll`)  
2. **Missing Dependency**:  
   `type_of(DefId(2:10))` (type definition of `Error`)  
3. **Root Cause**:  
   Normalization `Self::Error` → `Error` during new-solver goal evaluation (`evaluate_goal_in_task`) did not record a dependency edge to `type_of(Error)` due to missing `read_index` call after `with_anon_task`.  

**Evidence Chain**:  
- Dep graph from cfail1 shows no edge between `typeck_of(poll)` and `type_of(Error)`  
- `-Zincremental-info` confirms reuse of `typeck_of(poll)` in cfail2  
- `type_of(Error)` hash changed between revisions  
- Old solver's `read_index` call (observed in `SelectionContext::in_task`) is absent in new-solver's `with_cached_task`  

**Conclusion**:  
The ICE occurs because the `typeck_of` query for `S::poll` reused cached results without invalidating when its implicit dependency (`type_of(Error)`) changed. The dependency was never recorded due to unpropagated `DepNodeIndex` from goal evaluation.  

**Recommended Action**:  
Modify `with_cached_task` to call `read_index` on the returned `DepNodeIndex` (mirroring old solver behavior) to force dependency recording during normalization.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
