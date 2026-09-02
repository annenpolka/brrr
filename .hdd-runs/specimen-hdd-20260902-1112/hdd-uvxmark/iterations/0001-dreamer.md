### Field Report: Investigating Lock Identity in Case B

**Environment State:**  
Operating within the provided constraints—no local execution of untrusted checkouts. Relying solely on documented source excerpts, lock artifacts, and public issue details (astral-sh/uv#11479). Focused on failing revision `2bda549bcca67f06df602901ad9cdf30d35add00`.

---

### Step 1: Inspect Lock Artifact  
Review the `uv.lock` excerpt for `e3nn` dependencies:  
```toml
[[package]]
name = "e3nn"
dependencies = [
    { name = "sympy", version = "1.13.1", source = { registry = "https://pypi.org/simple" } },
    { name = "sympy", version = "1.13.3", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.2.0", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.5.1", source = { registry = "https://pypi.org/simple" } },
]
```

**Observation:**  
- `torch 2.5.1` has **no conflict marker** (omitted entirely).  
- `torch 2.2.0` retains an extras marker (`extra == '...'`).  

---

### Step 2: Analyze Code Behavior at Failing Revision  
Source excerpt (`simplify_conflict_markers_failing.rs`):  
```rust
for edge_index in (0..graph.edge_count()).map(EdgeIndex::new) {
    let (from_index, _) = graph.edge_endpoints(edge_index).unwrap();
    let Some(inference_sets) = inferences.get(&from_index) else {
        continue;
    };
    let all_paths_satisfied = inference_sets.iter().all(|set| {
        graph[edge_index].conflict().evaluate(&extras, &groups)
    });
    if !all_paths_satisfied {
        continue;
    }
    for set in inference_sets {
        for inf in set {
            if inf.included {
                graph[edge_index].assume_conflict_item(&inf.item);
            } else {
                graph[edge_index].assume_not_conflict_item(&inf.item);
            }
        }
    }
}
```

**Key Logic:**  
- For each dependency edge, check if **all inference sets** satisfy its conflict marker.  
- If satisfied:  
  - Call `assume_conflict_item`/`assume_not_conflict_item` to simplify the marker.  
- **Ambiguous edges** (e.g., two `torch` versions) are **not skipped**—processed unconditionally.  

---

### Step 3: Reconcile with Case B Scenario  
**Case B Setup:**  
- Pre-existing `uv.lock` generated *without* extras (e.g., `uv sync -p 3.12`).  
- Run `uv sync -p 3.12 --extra m3gnet` against this lock.  

**Observed Outcome (Public Issue):**  
- Installs both `torch 2.5.1` (unconditional) and `torch 2.2.0` (extra-gated).  
- Lock retains `torch 2.5.1` with **no marker** and `torch 2.2.0` with its marker.  

**Conflict Marker Simplification:**  
1. **Original Marker for `torch 2.5.1`:**  
   Inferred from `e3nn`'s dependency declarations (not shown in lock). Likely an extras marker (e.g., `extra != ...`).  
2. **Simplification Process:**  
   - `simplify_conflict_markers` evaluates the marker against all inference sets.  
   - If **all sets satisfy** the marker, it calls `assume_conflict_item`→**marker simplified to `true`**.  
   - Result: Marker **omitted** from lock output (treated as unconditional).  

---

### Step 4: Determine Identity for `e3nn→torch 2.5.1`  
- **Lock Representation:** Marker absent → **unconditional dependency**.  
- **Behavior:**  
  - Without extras (Case A): Only `torch 2.5.1` installed (expected).  
  - With `--extra m3gnet` (Case B): **Both `torch 2.5.1` and `2.2.0` installed**—indicating `2.5.1` is still considered unconditional.  

**Conclusion:**  
In Case B, the identity of `e3nn→torch 2.5.1` in `uv.lock` is **leftover unconditional (extras marker omitted)**.  

---

### Why Not Other Scenarios?  
- **Extra-Gated Marker?** No—marker was simplified to `true`/omitted. Lock shows no marker.  
- **Omitted Edge?** No—edge persists in lock and installs.  
- **Post-Repair Behavior (Cases C/D):** Irrelevant—failing revision lacks `ambiguous_edges > 1` skip.  

---

### Uncertainty Note  
Without runtime validation (prohibited), conclusions rely solely on:  
1. Lock artifact structure.  
2. Code logic at failing revision.  
3. Publicly observed install behavior.  

**Recommendation for Smaller Investigation:**  
Isolate the `simplify_conflict_markers` unit test with the `e3nn` dependency graph to verify marker simplification outcomes under extras activation.
