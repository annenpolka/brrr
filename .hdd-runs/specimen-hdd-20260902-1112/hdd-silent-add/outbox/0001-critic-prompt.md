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

        ### Field Report: Investigating Index Collision Failure in libgit2

**Situation**: After reviewing the reported issue (libgit2#7160) and associated PR 7332, I'm operating within a libgit2 development environment to understand why `git_index_add` succeeds despite unresolved path collisions when insertion occurs at non-zero positions. The environment includes libgit2 source and build artifacts, but I cannot execute the provided test case per constraints.

---

### Step 1: Code Inspection of Collision Detection
Ran source inspection focusing on `index.c` collision logic. Used the unfamiliar CLI `srcinspector` for cross-referencing call paths:

```bash
$ srcinspector find-function git_index_add --file=src/index.c
FOUND: git_index_add() @ src/index.c:1873
DEPENDENT LOGIC: 
  -> index_entry_cmp() [sorting]
  -> check_file_directory_collision() [conflict check]
  -> check_directory_file_collision() [conflict check]
```

```bash
$ srcinspector trace-calls check_directory_file_collision --file=src/index.c
TRACE: check_directory_file_collision() called by:
  git_index_add() @ index.c:1948 (after insertion position calculated)
PARAMETERS: 
  size_t position, const git_index_entry *entry
```

**Observation**: Collision checks trigger *after* calculating insertion position. The conflict detector only examines immediate siblings at the insertion point.

---

### Step 2: Simulate Non-Zero Insertion Failure Path
Reproduced the control flow without test execution by forcing debug logs into the collision checker. Modified `check_directory_file_collision()` temporarily:

```c
// DEBUG PATCH
GIT_INLINE(int) check_directory_file_collision(...) {
  // ... existing logic ...
  git_debug("COLLISION CHECK: position=%zu, pre-check=%s", 
            position, (position > 0 ? "ENABLED" : "SKIPPED"));
}
```

Rebuilt libgit2 locally:
```bash
$ make -C build debug
```

**Observation**: When `position > 0`, the function checks *only* index entries at `position-1` and `position+1`. No full ancestry validation occurs.

---

### Step 3: Validate Index State After Failed Collision Check
Used `idxdump` CLI (unfamiliar index inspection tool) to examine index state after simulated collision:

```bash
$ idxdump .git/index --filter=conflicts
ENTRY 0x7f8a3d604a10:
  path:   "a/prior_file"
  status: CONFLICT_NONE

ENTRY 0x7f8a3d604f30:
  path:   "conflicting_path"   # STALE DIRECTORY ENTRY
  status: CONFLICT_UNRESOLVED

ENTRY 0x7f8a3d605220:
  path:   "conflicting_path/new_blob"  # ADDED BLOB
  status: CONFLICT_POTENTIAL
```

**Observation**: Both the stale tree entry (`conflicting_path/`) and new blob (`conflicting_path/new_blob`) coexist post-`git_index_add`. The tool confirms:
- No cleanup of conflicting directory entry
- No ancestry validation beyond immediate siblings
- Success status results from missed multi-hop conflict check

---

### Step 4: Verify Position-Dependent Behavior
Forced insertion position to 0 via path manipulation:

```bash
$ idxmod .git/index --move-entry="conflicting_path" --to-position=0
$ lg2 add conflicting_path/new_blob  # libgit2 CLI
$ idxdump .git/index --filter=conflicts
ENTRY 0x7f8a3d604f30:
  path:   "conflicting_path"   # REMOVED
  status: CONFLICT_RESOLVED

ENTRY 0x7f8a3d605220:
  path:   "conflicting_path/new_blob"
  status: CONFLICT_NONE
```

**Observation**: When insertion occurs at position 0, the sibling check correctly removes the stale directory entry. Failure is position-dependent.

---

### Root Cause Confirmed
- **Why success reported**: Collision detection only examines *immediate* index neighbors. Distant conflicts (separated by other entries) bypass validation.
- **Conflicting entries**: Stale tree/blob remains at original position while new blob is inserted. Dump shows both present with conflict flags.
- **Position sensitivity**: At position 0, the single neighbor check catches conflicts. Non-zero positions allow "skip-over" failures.

**Unresolved Uncertainty**: Why the initial implementation omitted full ancestry traversal. No comments in source explain this constraint.

**Recommendation**: Adopt the PR 7332 approach of iterative ancestor checks, but note that recursive validation may impact performance for deep paths.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
