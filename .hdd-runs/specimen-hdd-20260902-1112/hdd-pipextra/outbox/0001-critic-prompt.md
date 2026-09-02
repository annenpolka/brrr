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

pip's resolvelib factory can treat a **link requirement that also names an extra** as a different identity from a constraint (or second request) on the same package without extras. Installing `pkg-1.0-py2.py3-none-any.whl[ext]` together with `pkg==1` (or an indirect `pkg2` that depends on `pkg1[ext]==1.0` plus an explicit `pkg1-1.0.whl[ext]` path) can fail to share the link candidate.

On failing_ref `a15dd75d98884c94a77d349b800c7c755d8c34e4`, `_make_candidate_from_link` builds a base `LinkCandidate` then, if extras are set, wraps it with `_make_extras_candidate`. `_make_requirements_from_install_req` for a path/link ireq with extras passes `extras=frozenset(ireq.extras)` into that function, so the **base** link candidate is not required separately. Constraints iterate `constraint.links` with `extras=frozenset()`.

Case A — path wheel without extras plus `pkg==1`:
  one link candidate, no extra wrap
  install succeeds
  no leftover extra identity

Case B — path wheel **with** extras plus a version constraint on the same name (`{wheel}[ext]` and `pkg==1`):
  failing_ref: extras candidate is not the same object the constraint looks up as the base link
  public: pip install local with extra fails dependency resolution (#12372)

Case C — two path wheels, `pkg2` depends on `pkg1[ext]==1.0`, plus explicit `{wheel_one}[ext]`:
  same leftover: extra on the explicit link is not applied on top of a shared base candidate
  in-tree after the repair: `test_new_resolver_constraint_on_link_with_extra_indirect`

Case D — extras only via specifier (`pkg[ext]==1.0`) with an index, no explicit link:
  not this leftover (no link candidate cache keyed without extras)

The developer wants to know which identity the factory stored for the explicit path: leftover extras-wrapped candidate that the constraint cannot reuse, a base link plus a second extras requirement, or omitted.

# OBSERVED

Public pypa/pip#12372 / PR 12392 (sanderr; merged 2023-12-17, merge `417ca92b439dba33d707b5da2493358863256bc3`). Failing world pinned on merge first parent `a15dd75d98884c94a77d349b800c7c755d8c34e4`. Local pip execution was not performed on this lab host.

PR body: extras handling where constraints on a package are not compatible with an explicit link candidate that also has an extra.

On failing_ref, `_make_candidate_from_link` returns `_make_extras_candidate(base, extras)` when extras are non-empty. `_make_requirements_from_install_req` for a link ireq passes those extras into that call, so only the extras-wrapped candidate is yielded. `find_candidates` for a later constraint/base request does not see that wrapped object as the explicit link base.

In-tree tests added on the PR (`test_new_resolver_constraint_on_link_with_extra`, `test_new_resolver_constraint_on_link_with_extra_indirect`) are **not** on the failing revision.

Not this packet: specimen-031 (pip empty extra). specimen-080 (owned extra marker fixture). pipmark (hdd-pipmark). `--require-hashes` extras #9644 / PR 9995. extras-on-error-message #13618 (unmerged #13659).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref a15dd75d98884c94a77d349b800c7c755d8c34e4
# src/pip/_internal/resolution/resolvelib/factory.py
# _make_candidate_from_link / _make_requirements_from_install_req

# public shape:
# pip install --no-index path/to/pkg-1.0-py2.py3-none-any.whl[ext] pkg==1
```

Source-backed only. Do not execute untrusted checkouts on the host.

pypa/pip
  src/pip/_internal/resolution/resolvelib/factory.py
  tests/functional/test_new_resolver.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  explicit path wheel pkg-1.0-py2.py3-none-any.whl
  extra name ext
  constraint pkg==1

Case A (path without extras + pkg==1):
  base link candidate
  no extras wrap
  install ok

Case B (path with extras + pkg==1):
  failing_ref extras-wrapped candidate
  constraint looks up base link with extras empty
  leftover: wrap is not the base

Case C (pkg2 depends pkg1[ext]==1.0 plus explicit pkg1.whl[ext]):
  same leftover on the explicit extra link

Case D (pkg[ext]==1.0 from index, no path link):
  not this leftover

Not this packet:
  pip empty extra (specimen-031)
  extra marker fixture (specimen-080)
  pipmark
  require-hashes extras (#9644)

### make_candidate_from_link_failing.py

# Reduced excerpt of _make_candidate_from_link on failing_ref
# src/pip/_internal/resolution/resolvelib/factory.py
# a15dd75d98884c94a77d349b800c7c755d8c34e4
# If extras are set, the returned candidate is the extras wrap, not the base link.

            base = self._link_candidate_cache[link]

        if not extras:
            return base
        return self._make_extras_candidate(base, extras, comes_from=template)

### make_requirements_failing.py

# Reduced excerpt of _make_requirements_from_install_req on failing_ref
# Link ireq passes extras into _make_candidate_from_link, so only the wrap is yielded.

            cand = self._make_candidate_from_link(
                ireq.link,
                extras=frozenset(ireq.extras),
                template=ireq,
                name=canonicalize_name(ireq.name) if ireq.name else None,
                version=None,
            )

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

        ### Field Report: Investigating Candidate Identity in pip's Resolver Factory

**Operational Context**:  
Using static analysis capabilities within the provided source fixture to examine resolvelib factory behavior. No local execution performed per security constraints. Focused on code paths from failing revision `a15dd75d988`.

---

### Step 1: Trace Explicit Path Handling  
Examined `_make_requirements_from_install_req` for explicit wheel path with extras (`pkg-1.0.whl[ext]`):

```python
# make_requirements_failing.py excerpt
cand = self._make_candidate_from_link(
    ireq.link,
    extras=frozenset(ireq.extras),  # extras=('ext',)
    template=ireq,
    name=canonicalize_name(ireq.name),
    version=None
)
yield cand
```
**Observation**:  
Explicit path requirement yields exactly one candidate – the extras-wrapped candidate. No base candidate is separately yielded.

---

### Step 2: Inspect Candidate Construction  
Traced `_make_candidate_from_link` call path:

```python
# make_candidate_from_link_failing.py excerpt
base = self._link_candidate_cache[link]  # Base candidate created/cached
if not extras:
    return base
return self._make_extras_candidate(base, extras)  # Wrapped candidate returned
```
**Observation**:  
1. Base candidate (`LinkCandidate`) created and stored in `_link_candidate_cache`  
2. With extras present: factory returns wrapped `ExtrasCandidate`  
3. **Key fact**: Base candidate exists in cache but isn't exposed to resolution  

---

### Step 3: Simulate Constraint Resolution  
Reconstructed constraint lookup flow (`pkg==1` requirement):

1. Constraint calls `find_candidates` with `extras=frozenset()`  
2. Factory checks candidate sources:  
   - **Explicit candidates**: Only wrapped candidate available (`ExtrasCandidate` for `pkg[ext]`)  
   - **Constraint lookup**: Seeks `LinkCandidate` (extras=None)  
3. Cache contains base candidate but isn't returned because:  
   - Not yielded by any requirement  
   - Not in active candidate pool  

**Failure Reproduction**:  
```log
# Simulated resolver output
Could not find candidate for pkg==1 (extras: none)
Available candidate: pkg==1.0 (extras: ['ext'])
```
**Observation**:  
Constraint fails because base candidate exists in cache but isn't surfaced to resolution layer.

---

### Step 4: Verify Identity Storage  
Inspected candidate registry state after processing explicit path:

| Candidate Type | Identity Key | Stored Where | Exposed to Resolver |
|----------------|-------------|-------------|---------------------|
| `LinkCandidate` | `(pkg, 1.0, frozenset())` | `_link_candidate_cache` | ❌ |
| `ExtrasCandidate` | `(pkg, 1.0, frozenset({'ext'}))` | Requirement yield | ✅ |

**Conclusion**:  
Factory stores **only extras-wrapped candidate** for explicit path requirement. Base candidate exists in private cache but isn't registered as available for reuse. This creates a "leftover" base candidate that constraints can't access.

---

### Step 5: Validate Against Cases  
**Case B/C Failure Confirmed**:  
- Explicit path with extras: yields wrapped candidate only  
- Constraint requires base candidate: can't see cached base candidate  
- Resolution fails due to missing base candidate  

**Case A Success Explained**:  
- Path without extras yields base candidate directly  
- Constraint reuses visible base candidate  

**Case D Irrelevance**:  
- No link candidate → no cache interaction  

---

### Artifact  
Candidate identity diagram generated from analysis:  
```
[Explicit Path Requirement]  
│  
└── Yields: ExtrasCandidate(pkg[ext])  
    │  
    └── Wraps: [Hidden] LinkCandidate(pkg)  // Inaccessible to constraints
```

**Final Observation**:  
The identity split occurs because the factory:  
1. Creates base candidate during link processing  
2. Fails to expose it when extras are present  
3. Leaves constraint requirements with no access path to base candidate  

No evidence found of secondary requirement generation or identity rewriting. Conflict stems from incomplete candidate exposure.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
