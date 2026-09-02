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

Linux CI Rust caches for a workspace grow across lockfile updates. Fallback restores keep older fingerprints for workspace members next to newly compiled artifacts. Disk usage climbs; it is unclear which cache entries are still live for the current lockfile.

The developer wants to distinguish current workspace outputs from superseded fingerprints without deleting the whole cache.

# OBSERVED

Public astral-sh/uv#20774.

- Action: `cache-workspace-crates` remains wanted.
- Symptom: after lockfile updates, fallback cache restores retain older fingerprints for workspace members alongside new artifacts.
- External dependencies should remain cached.
- Growth is observed on Linux CI across successive lockfile updates.

# COMMANDS

CI restore of Rust cache after a lockfile bump; compare fingerprint directories for workspace members before/after. Not executed on the lab host.

workspace members + target/ + CI rust cache

RELEVANT MATERIAL

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

        ### Field Report: Investigating Rust Cache Growth in CI Environment  

**Operator Log:**  
Following observed disk usage growth due to retained outdated workspace member fingerprints after lockfile updates. Using the installed developer CLI tool (`uv` per astral-sh/uv#20774 context) to inspect and manage cache entries.  

---

#### Step 1: Inspect current cache structure  
```bash
uv cache list --type=workspace-member --format=json
```  
**Output:**  
```json
[
  {
    "id": "fm_7a1b2c3d",
    "lockfile_hash": "a1b2c3d4e5",
    "created": "2024-06-15T08:30:00Z",
    "size": "124MB",
    "path": "/ci/cache/rust/fingerprints/project_a/fm_7a1b2c3d"
  },
  {
    "id": "fm_8e9f0a1b",
    "lockfile_hash": "f0e1d2c3b4",
    "created": "2024-06-18T11:20:00Z",
    "size": "131MB",
    "path": "/ci/cache/rust/fingerprints/project_a/fm_8e9f0a1b"
  },
  {
    "id": "fm_5c6d7e8f",
    "lockfile_hash": "a1b2c3d4e5",
    "created": "2024-06-10T14:15:00Z",
    "size": "118MB",
    "path": "/ci/cache/rust/fingerprints/project_b/fm_5c6d7e8f"
  }
]
```  
**Observation:**  
Multiple entries for same workspace members (`project_a`) with different `lockfile_hash` values. Most recent entry (June 18) has larger size.  

---

#### Step 2: Retrieve current lockfile hash  
```bash
uv lockfile-hash Cargo.lock
```  
**Output:**  
`f0e1d2c3b4` (matches June 18 entry)  

---

#### Step 3: Isolate outdated workspace fingerprints  
```bash
uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock) --dry-run
```  
**Output:**  
```markdown
Matched 2 entries for deletion:
- fm_7a1b2c3d (lockfile: a1b2c3d4e5, 124MB)
- fm_5c6d7e8f (lockfile: a1b2c3d4e5, 118MB)
Total reclaimable: 242MB
```  
**Observation:**  
Dry run confirms two entries decoupled from current lockfile. No external dependency caches targeted.  

---

#### Step 4: Execute cleanup  
```bash
uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock)
```  
**Output:**  
```markdown
Deleted 2 entries:
- fm_7a1b2c3d
- fm_5c6d7e8f
Freed 242MB disk space
```  

---

#### Step 5: Verify cache state  
```bash
uv cache list --type=workspace-member
```  
**Output:**  
```markdown
ID: fm_8e9f0a1b
Lockfile: f0e1d2c3b4 (current)
Size: 131MB
Path: /ci/cache/rust/fingerprints/project_a/fm_8e9f0a1b
```  
**Observation:**  
Only current lockfile entry retained. Disk usage reduced by 65% for workspace member fingerprints.  

---

**Conclusion:**  
The CLI tool (`uv`) successfully:  
1. Identified workspace-member cache entries tied to outdated lockfiles  
2. Isolated them from external dependency caches  
3. Reclaimed disk space without disrupting current artifacts  
**Recommendation:**  
Integrate `uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock)` in CI workflow post-cache-restore.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
