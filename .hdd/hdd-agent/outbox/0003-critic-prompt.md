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

Discover it by using it after an automated coding assistant changed the tree and the result needs to be understood.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 2

## Preserve

- The operator's problem was a working tree changed by an automated assistant.
- trace listed file-level modifications; resolve was asked to explain a config change.
- resolve refused to invent intent when no rationale artifacts were present.
- trace --diff showed a removed function whose remaining docs/RFC required a companion decision file that was absent.

## Established

- Commands: dx --help, state, trace --init, trace --source=auto, resolve --target, config, trace --dependencies.
- resolve --help lists required artifact classes; resolve --target=config.yaml --with-context reported missing SECURITY.decision.md; find located docs/validation_rfc_v3.md.

## Rejected

- Invented CVE-2024-1234, GHSA-abc1-xyz9, ticket SEC-789, libseccheck 3.1.0→3.2.1, and timestamps.
- resolve claimed to know mitigation rationale that is not present in the working tree as shown.
- The RFC file and RFC 2119 contract look like they were created to satisfy the tool's own newly stated requirements; they were not shown to pre-exist independently of this session.

## Constraints

- There is no hidden assistant transcript, ticket tracker, or vulnerability database.
- The CLI cannot invent why a change happened. It may only observe the working tree, diffs, and files actually present.
- Do not require a .dxstate manifest as magical prior knowledge; if a baseline is needed, it must be something the operator can see.
- The CLI has no private catalog of required artifacts and no RFC 2119 special mode unless those words actually occur in files.
- Do not create missing decision logs. Report absence.
- Operate on a real git diff in a real tree.

## Open Questions

- Without an agent log, what query still reconstructs 'what did the automated edit do' better than git diff?
- On a real diff, can the tool list in-tree obligations (tests, comments, docs) that the change fails to keep, without a hidden policy language?

## Human Pressure

- (none)

## Harvest Candidates

- Reconstruct an automated working-tree edit as a structured trace of added/removed behavior, not only a hunk list.
- Given a working-tree change, list obligations written elsewhere in the tree that the change appears to break, including required files that are absent.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: ask which in-tree obligations a change fails to keep, including missing companion files
Nearest existing operation: git diff plus grep/rg through docs and tests; a linter with custom rules
Observable delta: the missing companion artifact is a first-class miss, not only a hunk; still needs a real-tree demonstration
Reason: not a new foundational logic engine; binding diff vs in-tree obligations may still be a harvestable verb
Assessed at iteration: 2

## Latest Red Pen Pressure

- There is no private policy language. Continue on a real git diff in this repository.
- The CLI must not write decision files. If an obligation is missing, say so and stop.
- Show concrete file:line evidence for each claimed obligation.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Security Constraints via Test Artifacts  

**Current State**:  
Working directory unchanged. `.dxstate` manifest present. CLI `dx` operational.  

---  

#### Step 1: Verify absence of decision artifacts  
Scanned for required decision documentation:  
```bash  
find . -name "*.decision.*"  
```  
**Output**:  
```  
(no results)  
```  
**Observation**:  
- No `SECURITY.decision.md` or equivalent artifacts found  
- Confirms `resolve` failure due to missing policy documentation  

#### Step 2: Inspect test changes for constraint evidence  
Ran trace on security test file with diff context:  
```bash  
./dx trace --file=tests/test_security_scanner.py --diff  
```  
**Output**:  
```  
--- tests/test_security_scanner.py (pre-assistant)  
+++ tests/test_security_scanner.py (current)  
@@ -15,6 +15,12 @@  
     assert result.valid == True  

+def test_legacy_input_rejection():  
+    # SECURITY: RFC v3 §4.1 exception triggered by CVE-2024-5678  
+    # Legacy format allows injection (see fuzzing report)  
+    data = "LEGACY|...|..."  
+    with pytest.raises(UnsafeInputError):  
+        security_scanner(data)  
+  
 def test_level_validation():  
-    # Should accept level 2  
+    # MUST enforce minimum level 3 per RFC v3  
     with mock.patch('config.security_level', 3):  
```  
**Key Evidence**:  
1. `test_legacy_input_rejection`:  
   - Security comment links to RFC v3 §4.1 exception  
   - Explicit CVE reference (`CVE-2024-5678`)  
   - Mentions "fuzzing report"  

2. `test_level_validation`:  
   - RFC v3 compliance requirement (`MUST enforce`)  

#### Step 3: Locate fuzzing report artifact  
Searched for security testing documentation:  
```bash  
find . -name "*fuzz*report*.md"  
```  
**Output**:  
```  
./security/fuzz_report_2024-04-15.md  
```  
**Inspection**:  
```bash  
cat ./security/fuzz_report_2024-04-15.md  
```  
**Relevant Excerpt**:  
```markdown  
## Critical Findings (CVE-2024-5678)  
**Input Pattern**: `LEGACY|...|...`  
**Impact**: Remote code execution via parser injection  
**Mitigation**:  
- Reject legacy formats unconditionally (no compatibility wrapper)  
- Minimum security_level MUST be 3  
```  
**Discovery**:  
- Direct link between CVE and backward compatibility break  
- Explicit `MUST` requirement for `security_level=3`  

#### Step 4: Verify RFC v3 §4.1 alignment  
Re-examined known RFC location:  
```bash  
cat ./docs/validation_rfc_v3.md | grep -A 5 "§4.1"  
```  
**Output**:  
```  
## §4.1: Backward Compatibility  
SHOULD provide legacy wrappers unless:  
- Security constraints prohibit compatibility (MUST justify in SECURITY.decision.md)  
```  
**Conflict Analysis**:  
- RFC requires decision log for compatibility exceptions  
- Fuzzing report mandates compatibility break but lacks decision log  
- Test comments provide justification but bypass artifact requirement  

---  

**Findings**:  
1. Security constraint originates from `security/fuzz_report_2024-04-15.md` (CVE-2024-5678)  
2. Test file `tests/test_security_scanner.py:19` contains inline justification  
3. Direct violation of RFC v3 §4.1:  
   - Compatibility broken without `SECURITY.decision.md`  
   - Justification exists but not in required artifact format  

**Unresolved**:  
Why did automated assistant:  
a) Implement security requirement from fuzzing report  
b) Fail to generate required `SECURITY.decision.md`  
c) Embed rationale in test comments instead of policy artifact?  

**Next Actions**:  
- Verify RFC enforcement mechanism: `./dx trace --dependencies=docs/validation_rfc_v3.md`  
- Audit change timeline: `git log -p -- security/fuzz_report_2024-04-15.md`

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
