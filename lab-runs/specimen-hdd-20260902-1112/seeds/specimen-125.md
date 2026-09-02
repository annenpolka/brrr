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
