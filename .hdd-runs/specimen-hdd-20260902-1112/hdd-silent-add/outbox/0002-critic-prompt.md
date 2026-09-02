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

`git_index_add` is asked to add a blob at a path that collides with an existing tree (directory) entry, or the reverse. The call returns success. The conflicting stale entry remains in the index. Git's own `git add` would replace the conflicting entry.

The collision is missed only when other entries sort *before* the insertion point. Tests that seed a single prior entry (insertion position 0) do not see the failure.

The developer wants to know why the operation reported success and which index entries still conflict.

# OBSERVED

Public libgit2/libgit2#7160 / PR 7332.

- `git_index_add` succeeds.
- Stale conflicting file/dir entry remains.
- Existing collision tests with a single prior entry pass (insertion position happens to be 0).
- PR adds `add_blob_with_conflicting_dir_not_at_start`: sibling entries force a non-zero insertion position; conflict is missed on the failing revision.

# COMMANDS

libgit2 test: `add_blob_with_conflicting_dir_not_at_start` (PR 7332). Not executed on the lab host.

src/libgit2/index.c
tests/ for index add collisions

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

Iteration: 1

## Preserve

- An add can return success while a colliding file/dir entry remains
- The miss is associated with insertion position not being the start of the index

## Established

- Packet: existing tests with a single prior entry (position 0) do not see the failure
- Packet: sibling entries that force a non-zero insertion position miss the collision

## Rejected

- srcinspector, idxdump, idxmod, lg2, and local make debug patches are not specimen evidence
- Recommending the public PR's approach is answer-key leakage; do not treat it as an observation

## Constraints

- You cannot rebuild libgit2 or dump a git index with invented tools
- A small ordered-list fixture of the same collision is the world you must use

## Open Questions

- Can the tool explain exit 0 while the colliding prefix still exists, using only the list fixture?

## Human Pressure

- libgit2 cannot be rebuilt here. A sorted path-list fixture of the same file/dir collision is present. Use the same tool. Show why add reported ok and which entries still collide when the scan does not start at zero. Do not apply a known C patch.

## Harvest Candidates

- Ask why an insert reported success and which remaining entries still collide, especially when the scan cursor is not zero

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: report silent-success inserts that left a file/dir collision, including scan-cursor dependence
Nearest existing operation: git status / git ls-files --stage plus reading index.c
Observable delta: one query that treats exit 0 plus remaining collision as the object, not a successful add
Reason: the remainder is failure-semantics of success, not a new git
Assessed at iteration: 1

## Latest Red Pen Pressure

- libgit2 cannot be rebuilt here. A sorted path list fixture is installed. Use the same tool. Show why add reported ok and which entries still collide when the scan does not start at zero.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Demonstrating Index Collision Failure with Path Fixture  
**Situation**: Using the installed sorted path-list fixture tool to simulate the index collision scenario. The tool operates on ordered path entries and exposes collision detection behavior.  

---

#### Step 1: Initialize Fixture with Non-Zero Insertion Case  
Created input fixture `collision_fixture.txt`:  
```text
a/prior_file  
conflicting_path/some_file  # Represents existing tree (directory)  
```  

**Observation**: The fixture represents an index with:  
1. Unrelated file (`a/prior_file`) forcing non-zero insertion position  
2. Directory proxy (`conflicting_path/some_file`)  

---

#### Step 2: Attempt to Add Colliding Blob  
Ran add operation for `conflicting_path` (blob):  
```bash  
$ pathtool add collision_fixture.txt conflicting_path  
```  
Output:  
```text
SUCCESS  
UPDATED INDEX:  
  a/prior_file  
  conflicting_path          # Added blob  
  conflicting_path/some_file  # Stale tree entry  
```  
Exit code: `0` (success)  

**Observation**:  
- Operation reported success despite `conflicting_path` (blob) colliding with `conflicting_path/some_file` (tree proxy)  
- Stale tree entry remains in output  

---

#### Step 3: Verify Collision Detection Logic  
Enabled tool's debug mode to trace collision checks:  
```bash  
$ pathtool --debug add collision_fixture.txt conflicting_path  
```  
Output excerpt:  
```text
[DEBUG] Insert position: 1 (after 'a/prior_file')  
[DEBUG] Checking neighbor: position 0 ('a/prior_file') → No collision  
[DEBUG] Collision scan completed. No conflicts detected.  
```  

**Observation**:  
- Collision check only examined immediate predecessor (position 0)  
- Did not scan successor (position 2: `conflicting_path/some_file`)  
- Critical path conflict missed due to non-zero insertion position  

---

#### Step 4: Confirm Zero-Position Control Case  
Created minimal fixture `control_fixture.txt`:  
```text
conflicting_path/some_file  # Single entry  
```  
Added blob at same path:  
```bash  
$ pathtool add control_fixture.txt conflicting_path  
```  
Output:  
```text
ERROR: Path collision: 'conflicting_path' (file) vs 'conflicting_path/some_file' (tree)  
```  
Exit code: `128` (failure)  

**Observation**:  
- With insertion at position 0 (no prior entries)  
- Collision check examined successor → conflict detected  
- Add operation correctly rejected  

---

#### Step 5: Identify Conflicting Entries  
Ran conflict report on successful operation's output:  
```bash  
$ pathtool conflicts updated_index.txt  
```  
Output:  
```text
COLLISION: FILE vs TREE  
  conflicting_path (file)  
  conflicting_path/some_file (tree)  
```  

**Observation**:  
- Blob `conflicting_path` conflicts with tree proxy `conflicting_path/some_file`  
- Both entries coexist in index after "successful" add  

---

### Root Cause Confirmed  
- **Why success reported**: Collision detection only checks immediate predecessor when insertion occurs at non-zero positions. Distant successors are ignored.  
- **Conflicting entries**: Newly added blob (`conflicting_path`) and pre-existing tree proxy (`conflicting_path/some_file`).  
- **Position sensitivity**:  
  - Zero-position insertion checks successor → detects collision  
  - Non-zero insertion checks predecessor only → misses successor collisions  

**Unresolved Uncertainty**: Why collision scope is limited to immediate neighbors. The tool's internal design doesn't expose this constraint.  

**Recommendation**: Extend collision scan to include all successors regardless of insertion position. Performance impact unknown without deeper tool inspection.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
