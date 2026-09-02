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

Task's checksum fingerprint can keep the identity of a **wildcard template** after two different MATCH instantiations should be different tasks. `.task/checksum/<name>` is keyed by the template name (`build-*`), so leftover checksum from `build-foo` is reused as up-to-date for `build-bar`.

On failing_ref `1e2121a99f6414e3bf4565e5736a116bef10be91`, compiled tasks keep `Task: origTask.Task` (the pattern). `Name()` / `LocalName()` do not include MATCH. `fingerprint.IsTaskUpToDate` uses that name as the cache key. Wildcard parameter is omitted from fingerprint identity.

Public report (go-task/task#1795): automatically concat the wildcard parameter on the cache key. Discussion #1794: two wildcard instantiations share one checksum.

In-tree after the repair (not on failing_ref): `FullName` replaces `*` with MATCH; `Name()` / `LocalName()` use FullName; testdata `build-*` writes `.task/checksum/build-wildcard`.

Case A — first `task build-foo` (checksum method):
  checksum written for the template name
  not leftover yet

Case B — later `task build-bar` with leftover checksum from foo:
  leftover: up-to-date identity of foo
  MATCH bar omitted from the key

Case C — non-wildcard `build` with its own checksum file:
  unique key
  not this leftover

Case D — delete `.task/checksum` then run bar:
  fresh identity
  not leftover fingerprint

The developer wants to know which identity case B actually left in `.task/checksum/`: leftover foo checksum reused as bar, separate bar checksum, or omitted (no checksum file).

# OBSERVED

Public go-task/task#1795 (closed 2025-09-11). PR 1808 squash `48039be12cdfc6b6871dbe9f1d6977027d660889` (parent `1e2121a99f6414e3bf4565e5736a116bef10be91`). Local task was not performed on this lab host.

Issue: wildcard parameter is not on the fingerprint cache key. Two MATCH instantiations share leftover checksum identity.

On failing_ref, compiledTask copies origTask.Task as the name. MATCH is a var, not the checksum key. FullName is **not** on the failing revision. It is added by PR 1808 (`fullName` replaces `*` with MATCH; `Name()` prefers FullName).

Not this packet: specimen-076/088/104 (gradle compiler fingerprints). pants leftover fingerprint (job-0464 hunt: no leftover-identity merged pair). cargo leftover (091/099/101).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 1e2121a99f6414e3bf4565e5736a116bef10be91
# variables.go compiledTask / taskfile/ast/task.go Name

# public shape:
# leftover .task/checksum/build-* from build-foo
# task build-bar reports up-to-date
```

Source-backed only. Do not execute untrusted checkouts on the host.

go-task/task
  variables.go
  taskfile/ast/task.go
  testdata/checksum/Taskfile.yml

RELEVANT MATERIAL

### compiled_task_name_failing.go

// Reduced excerpt of compiledTask / Name on failing_ref
// variables.go / taskfile/ast/task.go
// 1e2121a99f6414e3bf4565e5736a116bef10be91
// Task name is the template. MATCH is not the checksum key.

	new := ast.Task{
		Task: origTask.Task,
		// no FullName
	}

func (t *Task) Name() string {
	if t.Label != "" {
		return t.Label
	}
	return t.Task
}

### leftover_identity_split.txt

Registry / fixture:
  tasks:
    build-*:
      method: checksum
  leftover .task/checksum from build-foo

Case A (first build-foo):
  checksum written for template name
  not leftover yet

Case B (later build-bar, leftover foo checksum):
  leftover: up-to-date identity of foo
  MATCH bar omitted

Case C (non-wildcard build):
  unique key
  not this leftover

Case D (delete .task/checksum):
  fresh identity
  not leftover fingerprint

Not this packet:
  gradle compiler fingerprints (specimen-076/088/104)
  pants leftover fingerprint (no merged pair)

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

        ### Field Report: Wildcard Checksum Identity Investigation  

**Operational Context**  
Using the installed `task` CLI (go-task/task at failing_ref `1e2121a99f`). Environment constraints prevent executing untrusted checkouts, so analysis relies on source inspection and documented behavior.  

---

#### Step 1: Inspect Cache Key Logic  
*Command:* Analyze `variables.go` and `taskfile/ast/task.go` at failing_ref.  
*Observation:*  
```go
// From variables.go (compiledTask):  
new := ast.Task{  
    Task: origTask.Task, // Retains wildcard template name (e.g., "build-*")  
    // No FullName field present  
}  

// From taskfile/ast/task.go (Name):  
func (t *Task) Name() string {  
    if t.Label != "" {  
        return t.Label  
    }  
    return t.Task // Returns template name ("build-*"), ignoring MATCH  
}  
```  
*Finding:* Fingerprint cache key is `Task.Name()` (template name). Wildcard parameter (`foo`/`bar`) is excluded.  

---

#### Step 2: Simulate Case B Behavior  
*Scenario:*  
- `.task/checksum/build-*` exists from prior `task build-foo` (Case A).  
- Run `task build-bar`.  

*Command:* Trace checksum lookup logic via source:  
```go  
// fingerprint.IsTaskUpToDate(key) uses:  
key := task.Name() // "build-*" for ANY wildcard instantiation  
```  
*Observation:*  
- `build-bar` uses **identical cache key** (`build-*`) as `build-foo`.  
- Tool finds existing `.task/checksum/build-*` and treats `build-bar` as up-to-date.  
- No new checksum file created for `bar`.  

---

#### Step 3: Verify Artifact State  
*Command:* Infer filesystem outcome:  
```bash  
# After Case A:  
$ ls .task/checksum  
build-*  # Checksum for 'foo'  

# After Case B (task build-bar):  
$ ls .task/checksum  
build-*  # Same file, unchanged  
```  
*Finding:*  
- Only `build-*` exists. No `build-bar` file created.  
- Checksum content remains the `foo` instantiation's fingerprint.  

---

#### Step 4: Conflict Check with Known Fix  
*Observation:*  
Post-fix (PR 1808) introduces `FullName`:  
```go  
// Fixed logic:  
key := task.FullName() // "build-foo" or "build-bar"  
```  
*Contrast with Case B:*  
- Failing_ref **lacks `FullName`**.  
- Wildcard instantiations **share single cache key** (`build-*`).  
- Leftover artifact: **Only `build-*` file exists**, reused for all instantiations.  

---

#### Conclusion  
For **Case B** (`task build-bar` with leftover `build-foo` checksum):  
- **Identity in `.task/checksum/`:** Leftover `build-*` file (from `foo`).  
- **State:** Single file persists; no per-instantiation checksum created.  
- **Mechanism:** Cache key omission of MATCH parameter causes reuse.  

**Evidence Chain:**  
1. Source confirms cache key = `Task.Name()` (template name).  
2. Issue #1795 verifies shared checksum across instantiations.  
3. Fix (PR 1808) explicitly corrects key to include MATCH.  

**Uncertainty:** Filesystem state inferred from source/logic (direct execution prohibited).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
