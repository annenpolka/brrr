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

uv's lock can keep the identity of a **previous extra-gated package version as unconditional** after a later extra activation should have been a different lock object. `simplify_conflict_markers` treats extras-known-to-be-enabled inferences as always-true, so an extras conflict marker is omitted (simplified to `true`) from `uv.lock`.

On failing_ref `2bda549bcca67f06df602901ad9cdf30d35add00`, `simplify_conflict_markers` walks every edge and, if all inference sets satisfy the conflict marker, calls `assume_conflict_item` / `assume_not_conflict_item`. Ambiguous edges (two outgoing edges with the same package name, e.g. sympy 1.13.1 and sympy 1.13.3) are **not** skipped.

Public report (astral-sh/uv#11479). `uv sync -p 3.12` installs only `torch==2.5.1`. `uv sync -p 3.12 --extra m3gnet` installs both `torch==2.2.0` and leftover `torch==2.5.1`, plus two sympy versions. Lock excerpt for always-required `e3nn`:

```
[[package]]
name = "e3nn"
dependencies = [
    { name = "sympy", version = "1.13.1", source = { registry = "https://pypi.org/simple" } },
    { name = "sympy", version = "1.13.3", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.2.0", source = { registry = "https://pypi.org/simple" }, marker = "extra == 'extra-4-test-alignn' or extra == 'extra-4-test-m3gnet'" },
    { name = "torch", version = "2.5.1", source = { registry = "https://pypi.org/simple" } },
]
```

The extras marker for sympy 1.13.1 / torch 2.5.1 was simplified to true. Those versions are leftover unconditional identity.

In-tree after the repair (not on failing_ref): skip simplification when `ambiguous_edges > 1`; test `duplicate_torch_and_sympy_because_of_wrong_inferences`.

Case A — `uv sync` with no extras (production only):
  torch 2.5.1 is the production identity
  not leftover extras-marker identity

Case B — `uv sync --extra m3gnet` with leftover lock that omitted extras markers:
  leftover: torch 2.5.1 / sympy 1.13.1 as unconditional
  extras marker omitted from lock identity
  also installs torch 2.2.0 / sympy 1.13.3 (extra-gated)

Case C — lock written with extras markers kept (post-repair shape, not on failing_ref):
  extra-gated versions stay extra-gated
  not leftover unconditional identity

Case D — delete `uv.lock` then `uv lock` with extras declared as conflicts:
  fresh lock identity
  not leftover simplified-to-true markers

The developer wants to know which identity case B actually left in `uv.lock` for e3nn→torch 2.5.1: leftover unconditional (extras marker omitted), extra-gated marker for m3gnet, or omitted (no torch 2.5.1 edge).

# OBSERVED

Public astral-sh/uv#11479 (closed 2025-02-18). PR 11513 rebase tip `91593d42d990397695a15750dcb8453c62a71b7d` (series parent `2bda549bcca67f06df602901ad9cdf30d35add00`). Local uv was not performed on this lab host.

Issue body: `uv sync --extra m3gnet` installs two torch versions and two sympy versions because some e3nn edges have extras conflict markers simplified to true.

On failing_ref, `simplify_conflict_markers` does not skip ambiguous same-name edges. `assume_conflict_item` can drop the extras marker from lock identity. The skip for `ambiguous_edges > 1` is **not** on the failing revision. It is added by PR 11513.

Not this packet: extraedge / specimen-080 / specimen-098 extras CLI. specimen-006 (uv CI cache leftover fingerprints). specimen-102 (uv leftover git vs directory in lock). specimen-106 (pdm extra path URL expanded). specimen-123/124 earthly leftover CACHE --id unexpanded ARG.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 2bda549bcca67f06df602901ad9cdf30d35add00
# crates/uv-resolver/src/graph_ops.rs simplify_conflict_markers

# public shape:
# leftover e3nn -> torch 2.5.1 with extras marker omitted (true)
# uv sync --extra m3gnet installs torch 2.2.0 AND leftover 2.5.1
```

Source-backed only. Do not execute untrusted checkouts on the host.

astral-sh/uv
  crates/uv-resolver/src/graph_ops.rs
  crates/uv-resolver/src/resolution/output.rs
  crates/uv/tests/it/lock_conflict.rs
  uv.lock

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  pyproject extras chgnet/sevennet/all/alignn/m3gnet with conflicts
  leftover uv.lock e3nn -> torch 2.5.1 / sympy 1.13.1 with extras marker omitted

Case A (uv sync, no extras):
  torch 2.5.1 production identity
  not leftover extras-marker

Case B (uv sync --extra m3gnet, leftover true markers):
  leftover: torch 2.5.1 / sympy 1.13.1 unconditional
  also extra-gated torch 2.2.0 / sympy 1.13.3
  extras marker omitted from lock identity

Case C (extras markers kept on ambiguous edges):
  extra-gated stay extra-gated
  not leftover unconditional

Case D (delete uv.lock then lock):
  fresh identity
  not leftover simplified-to-true

Not this packet:
  extraedge / specimen-080 / specimen-098 extras CLI
  uv CI cache leftover fingerprints (specimen-006)
  uv leftover git vs directory (specimen-102)
  pdm extra path URL expanded (specimen-106)
  earthly leftover CACHE --id unexpanded ARG (specimen-123/124)

### simplify_conflict_markers_failing.rs

// Reduced excerpt of simplify_conflict_markers on failing_ref
// crates/uv-resolver/src/graph_ops.rs
// 2bda549bcca67f06df602901ad9cdf30d35add00
// Ambiguous same-name edges are not skipped.
// Extras inferences can simplify a conflict marker to true.

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
