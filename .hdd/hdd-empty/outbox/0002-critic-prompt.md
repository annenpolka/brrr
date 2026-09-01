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

        An unfamiliar developer CLI is already installed in this environment.

Discover it by using it on a development query that might legitimately return nothing.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- A deliberate non-matching query printed 0 matches and claimed success rather than an error.
- The operator treated empty as a legitimate outcome.

## Established

- query, query --context, env.

## Rejected

- 847 artifacts, v3.1.0, 30-day index are unsupported.

## Constraints

- No hidden project index. Search real files in this tree.
- Empty, error, and unknown/unindexed must be distinguishable (message and exit code).
- Do not invent scan counts.

## Open Questions

- On a real tree, is empty-vs-error-vs-unknown a distinct contract from grep/rg?

## Human Pressure

- (none)

## Harvest Candidates

- A search whose empty result is success, with a different exit for errors and for 'this query cannot be answered here'.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: search a tree and treat zero hits as a successful empty, distinct from failure
Nearest existing operation: rg (exits 1 on no match) or find
Observable delta: empty is not a failure; not yet shown with a third unknown state on a real tree
Reason: worth one local turn; do not add a tracing index
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no artifact index. Continue using the same CLI on real files in this directory.
- Zero hits must be distinguishable from I/O errors and from 'cannot answer'.
- Do not print invented scan counts.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Operating the Unfamiliar Developer CLI (Continuation)  

**Command Attempt 5:**  
Re-ran `env` to verify environment after correction about index:  
```  
$ dev env  
[ENVIRONMENT]  
Project: /repos/service-alpha  
Artifacts: code, logs, traces (live scan)  
```  
**Observation:**  
- Previous index/delta-updates metadata removed. Now explicitly states "live scan".  
- Version/temporal constraints absent. Confirms artifact scanning occurs in real-time.  

---  

**Command Attempt 6:**  
Tested `query` with non-matching pattern to observe revised output:  
```  
$ dev query __no_such_pattern__  
[QUERY] Pattern: "__no_such_pattern__"  
[RESULT] 0 matches.  
```  
**Observation:**  
- Artifact scan count (previously "Scanned: 847") removed per correction.  
- Exit code remains `0` (verified). Empty results still explicitly declared.  

---  

**Command Attempt 7:**  
Provoked I/O error by querying unwritable directory:  
```  
$ dev query "test" --context /locked_dir  
[QUERY] Pattern: "test" (context: /locked_dir)  
[STATUS] ERROR: Permission denied (os error 13)  
```  
**Exit Code:** `3` (verified via `echo $?`)  
**Observation:**  
- Differentiated error case: Explicit "ERROR" label with OS-level details.  
- Non-zero exit code (`3`). Consistent with requirement to distinguish errors from empty results.  

---  

**Command Attempt 8:**  
Tested malformed pattern syntax to trigger "cannot answer" state:  
```  
$ dev query "*.js["  
[QUERY] Pattern: "*.js["  
[STATUS] ERROR: Invalid pattern syntax (unclosed bracket)  
```  
**Exit Code:** `2`  
**Observation:**  
- Unique exit code (`2`) and error type ("Invalid pattern syntax").  
- Distinguishable from I/O errors (`exit 3`) and empty results (`exit 0`).  

---  

**Command Attempt 9:**  
Verified `trace` command with invalid ID:  
```  
$ dev trace invalid_id99  
[TRACE] Requested ID: invalid_id99  
[RESULT] No chain found for trace ID.  
```  
**Exit Code:** `0`  
**Observation:**  
- Empty trace result treated same as `query`: Explicit "No chain found", success exit code.  
- Consistent empty-result semantics across commands.  

---  

**Conclusions:**  
1. **Error Differentiation Confirmed:**  
   - I/O errors: `exit 3` + OS details  
   - Syntax errors: `exit 2` + validation message  
   - Empty results: `exit 0` + explicit "0 matches"/"No chain found"  
2. **Live Scanning:** Artifact counts omitted post-correction. Environment reflects real-time file operations.  
3. **Pattern Handling:** Malformed patterns yield validation errors (not silent empty results).  

**Unresolved:**  
- Scope of "live scan": Does it traverse nested directories?  
- How `--context` modifies search depth/behavior without scan counts.  

**Next Step:**  
Test `query` with valid pattern across directory hierarchy to observe traversal behavior.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
