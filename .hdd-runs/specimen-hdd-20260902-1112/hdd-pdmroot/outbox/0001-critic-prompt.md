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

`pdm lock --update-reuse` of a project that names a **local path extra** can rewrite that extra's lock identity from a portable `${PROJECT_ROOT}` URL to a **machine-absolute `file:///` URL**, even when the lock `path` field stays relative.

Public report (pdm-project/pdm#2852). Monorepo:

```
my-repo/
  app/   pyproject + pdm.lock   depends on "lib[test] @ file:///${PROJECT_ROOT}/../lib"
  lib/   pyproject
```

On failing_ref `cc17967ace76ff2fdf455106a6eb26da50685260`, first `pdm lock` writes:

```
[[package]]
name = "lib"
version = "0.1.0"
extras = ["test"]
path = "../lib"
dependencies = [
    "lib @ file:///${PROJECT_ROOT}/../lib",
    "pytest",
]
```

Immediately afterwards, `pdm lock --update-reuse` rewrites the extra line to an expanded absolute URL:

```
    "lib @ file:///mnt/c/pdm-minimal/lib",
```

`format_lockfile` only attempted `relative_to(project.root)` when `FileRequirement.path` was already absolute. Extra-require handling mutated the shared `install_requires` list (`self._data.install_requires` without a copy), so a later reuse pass saw a different URL identity than the first lock.

Case A — no extras, only a path dep `lib @ file:///${PROJECT_ROOT}/../lib`:
  `--update-reuse` keeps the variable URL
  no leftover expansion

Case B — extra `lib[test]` path dep, `pdm lock` then `pdm lock --update-reuse`:
  first lock: portable `${PROJECT_ROOT}` URL + relative `path`
  failing_ref reuse: leftover absolute `file:///...` URL next to the same relative `path`
  leftover identity: expanded URL vs portable PROJECT_ROOT URL

Case C — extra deps that are registry names (pytest), not path:
  no file URL to expand
  not this leftover

Case D — `pdm lock` without `--update-reuse` after a clean tree:
  first-write identity only
  not the reuse leftover

The developer wants to know which identity case B actually stored for the extra path dep after `--update-reuse`: leftover expanded absolute URL, the portable `${PROJECT_ROOT}` URL, or omitted.

# OBSERVED

Public pdm-project/pdm#2852 closed 2024-05-08. PR 2874 merge `931de2106b37e8dc55efb84de6bf7a704ad28842` (parent `cc17967ace76ff2fdf455106a6eb26da50685260`). Title: keep `${PROJECT_ROOT}` after `pdm lock --update-reuse`. Local PDM execution was not performed on this lab host.

On failing_ref, `format_lockfile` (src/pdm/cli/utils.py):

```
if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
    try:
        r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
        r.url = backend.relative_path_to_url(r.path.as_posix())
    except ValueError:
        pass
```

Relative `path = "../lib"` skipped the rewrite. Extra-require assembly used `result = self._data.install_requires` (same list object) then appended extras, so reuse could emit an expanded URL while `path` stayed relative.

News file `news/2852.bugfix.md` is **absent** on `cc17967ace76ff2fdf455106a6eb26da50685260`. It is added by PR 2874.

Not this packet: specimen-006/022/023/102 (uv git vs directory source kinds / Poetry path inside git checkout). specimen-021 (poetry extras). specimen-031/098 (pip extras-on-link).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref cc17967ace76ff2fdf455106a6eb26da50685260
# src/pdm/cli/utils.py format_lockfile FileRequirement branch
# src/pdm/models/setup.py extras_require vs install_requires

# public shape:
# pdm lock
#   path = "../lib"
#   "lib @ file:///${PROJECT_ROOT}/../lib"
# pdm lock --update-reuse
#   path = "../lib"
#   failing: "lib @ file:///mnt/c/pdm-minimal/lib"
```

Source-backed only. Do not execute untrusted checkouts on the host.

pdm-project/pdm
  src/pdm/cli/utils.py
  src/pdm/models/setup.py
  news/2852.bugfix.md

RELEVANT MATERIAL

### format_lockfile_failing.py

# Reduced excerpt of format_lockfile on failing_ref
# cc17967ace76ff2fdf455106a6eb26da50685260
# URL rewrite runs only when path is already absolute.

        deps: list[str] = []
        for r in fetched_dependencies[v.dep_key]:
            if isinstance(r, FileRequirement) and r.path and r.path.is_absolute():
                try:
                    r.path = Path(os.path.normpath(r.path)).relative_to(os.path.normpath(project.root))
                    r.url = backend.relative_path_to_url(r.path.as_posix())
                except ValueError:
                    pass
            deps.append(r.as_line())

### leftover_identity_split.txt

Registry / fixture:
  app depends on lib[test] @ file:///${PROJECT_ROOT}/../lib
  lib is a sibling path package

Case A (path dep, no extras):
  --update-reuse keeps ${PROJECT_ROOT}
  no leftover expansion

Case B (extra lib[test], lock then --update-reuse):
  first lock: file:///${PROJECT_ROOT}/../lib + path ../lib
  failing reuse: file:///mnt/c/pdm-minimal/lib + path ../lib
  leftover: expanded URL vs portable PROJECT_ROOT URL

Case C (registry extra pytest):
  no file URL
  not this leftover

Case D (first pdm lock only):
  first-write identity
  not reuse leftover

Not this packet:
  uv git vs directory (specimen-006/022/023/102)
  pip extras-on-link (specimen-098)

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

        Based on the provided environment constraints and observed behavior, I'll operate within the known facts to investigate the identity stored after `pdm lock --update-reuse` in Case B:

**Concrete Reproduction Attempt (within known constraints):**
```bash
# Attempt to inspect lockfile state without execution
cd my-repo/app

# Capture initial lock state
cat pdm.lock | grep -A5 'name = "lib"'
# Observed output (first lock):
# [[package]]
# name = "lib"
# version = "0.1.0"
# extras = ["test"]
# path = "../lib"
# dependencies = [
#     "lib @ file:///${PROJECT_ROOT}/../lib",

# Run update with reuse
pdm lock --update-reuse

# Inspect changed dependency line
cat pdm.lock | grep "lib @ file://"
# Observed output (on failing_ref):
#     "lib @ file:///mnt/c/pdm-minimal/lib",
```

**Investigation of Conflict:**  
The key conflict is between two observations:
1. `format_lockfile` only processes absolute paths (relative paths skip the URL rewrite)
2. The extra dependency shows an absolute URL despite relative path entry

**Source Code Correlation:**  
Examining `src/pdm/models/setup.py` (not executed, read-only inspection):
```python
# In RequirementSet.add_extra() (hypothesized location):
def add_extra(self, name: str) -> None:
    # Public issue suggests this mutates install_requires directly
    result = self._data.install_requires  # Shared reference!
    # ... extra handling appends to same list
```

**Behavioral Deduction:**  
1. First `pdm lock` creates requirement with portable URL  
2. `--update-reuse` loads requirement objects from memory  
3. Requirement's URL field gets expanded during reuse resolution  
4. `format_lockfile` sees relative path → skips URL rewrite  
5. Lock writes expanded URL from memory object + unchanged relative path  

**Identity Storage Confirmation:**  
After `pdm lock --update-reuse` in Case B:  
- ✅ Lockfile contains **absolute `file:///` URL**  
- ✅ Path remains relative (`../lib`)  
- ❌ Portable `${PROJECT_ROOT}` is lost  

**Failed Mitigation Attempt:**  
```bash
# Try to force portable format (should fail on failing_ref)
pdm lock --no-reuse
# Output: Reverts to portable URL (Case D behavior)
# But violates --update-reuse requirement

# Attempt to sanitize lockfile manually (outside tool scope)
sed -i 's|file:///.*/lib|file://${PROJECT_ROOT}/../lib|' pdm.lock
pdm lock --update-reuse
# Output: Absolute URL reappears - proves mutation occurs in-memory
```

**Conclusion from Observations:**  
The reuse operation stores the **expanded absolute URL** for extra path dependencies while preserving the relative path field. This creates a hybrid state not present in first-time locks. The fix (PR#2874) addresses this by decoupling the requirement mutation during extra handling.

---

**Field Report Summary:**  
`pdm lock --update-reuse` on commit `cc17967ace` with local path extras:  
- Lock identity: **Machine-absolute file URL** (`file:///path/to/lib`)  
- Path field: **Unchanged relative path** (`../lib`)  
- Artifact: Non-portable lockfile with conflicting location indicators  
- Resolution: Requires tool fix (implemented in later commit) as workflow adjustments cannot prevent in-memory mutation

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
