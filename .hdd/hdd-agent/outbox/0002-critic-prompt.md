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

Iteration: 1

## Preserve

- The operator's problem was a working tree changed by an automated assistant.
- trace listed file-level modifications; resolve was asked to explain a config change.

## Established

- Commands: dx --help, state, trace --init, trace --source=auto, resolve --target, config, trace --dependencies.

## Rejected

- Invented CVE-2024-1234, GHSA-abc1-xyz9, ticket SEC-789, libseccheck 3.1.0→3.2.1, and timestamps.
- resolve claimed to know mitigation rationale that is not present in the working tree as shown.

## Constraints

- There is no hidden assistant transcript, ticket tracker, or vulnerability database.
- The CLI cannot invent why a change happened. It may only observe the working tree, diffs, and files actually present.
- Do not require a .dxstate manifest as magical prior knowledge; if a baseline is needed, it must be something the operator can see.

## Open Questions

- Without an agent log, what query still reconstructs 'what did the automated edit do' better than git diff?

## Human Pressure

- (none)

## Harvest Candidates

- Reconstruct an automated working-tree edit as a structured trace of added/removed behavior, not only a hunk list.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: summarize what an automated edit changed in a working tree and what behavior disappeared
Nearest existing operation: git diff / git status / reading the assistant's own chat log
Observable delta: not yet shown: a trace of removed behavior (validate_input gone with no wrapper) as a first-class object rather than a hunk
Reason: rationale-from-CVE is magic; a behavioral trace of an uncommitted automated edit may still be a composition worth testing
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no assistant transcript, CVE database, or ticket system. Continue using the same CLI on a real working tree that an editor or script just changed.
- The CLI cannot explain intent. Show only added, removed, or rewritten observable behavior.
- Do not create a hidden manifest that already knows the answer. If a baseline is required, the operator must be able to point at it.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Re-examining Changes with Observable Constraints  

**Current State**:  
Working directory unchanged from prior report. `.dxstate` manifest present. CLI `dx` remains operational.  

---  

#### Step 1: Verify CLI command constraints  
Re-ran help with focus on `resolve` parameters:  
```bash  
./dx resolve --help  
```  
**Output**:  
```  
resolve - Explain changes via observable artifacts  

USAGE:  
  resolve --target=PATH [--with-context]  

REQUIRES:  
  Changes must be reflected in:  
    - Code comments containing RFC 2119 keywords (MUST, SHOULD, etc)  
    - Git commit messages (if VCS baseline available)  
    - Markdown decision logs (*.decision.md)  
```  
**Discovery**:  
- `resolve` depends exclusively on *present* artifacts  
- No external vulnerability/ticket integration  

#### Step 2: Re-attempt config change rationale  
Ran resolve against config.yaml with context flag:  
```bash  
./dx resolve --target=config.yaml --with-context  
```  
**Output**:  
```  
No supported rationale artifacts found for config.yaml:  
  - Missing: SECURITY.decision.md  
  - Missing: commit message metadata  
```  
**Failure Analysis**:  
- CLI requires explicit decision documentation  
- Automated assistant left no observable rationale  

#### Step 3: Inspect code changes directly  
Used `trace` to extract modified function context:  
```bash  
./dx trace --file=src/main.py --diff  
```  
**Output**:  
```  
--- src/main.py (pre-assistant)  
+++ src/main.py (current)  
@@ -42,7 +42,7 @@  
- def validate_input(data):  
-     # DEPRECATED: Use security_scanner instead  
-     return basic_check(data)  
+  
+ def security_scanner(data):  
+     # Implements validation RFC v3  
+     return advanced_check(data, level=config.security_level)  
```  
**Observation**:  
- Removal of `validate_input()` accompanied by deprecation comment  
- New `security_scanner()` references RFC (unverified)  

#### Step 4: Validate RFC reference  
Searched working tree for RFC documentation:  
```bash  
find . -name '*rfc*.md'  
```  
**Output**:  
```  
./docs/validation_rfc_v3.md  
```  
**Inspection**:  
```bash  
cat ./docs/validation_rfc_v3.md  
```  
**Relevant Excerpt**:  
```markdown  
## Section 4.1: Backward Compatibility  
SHOULD provide legacy wrappers unless:  
- Security constraints prohibit compatibility (MUST justify in SECURITY.decision.md)  
```  
**Discovery**:  
- RFC exists but requires companion security decision log  
- No `SECURITY.decision.md` found in project  

---  

**Findings**:  
1. `resolve` command fails without explicit decision artifacts  
2. Deprecation comment suggests planned obsolescence  
3. RFC v3 mandates backward-compatibility wrappers *unless* security-justified  
4. Critical gap: Missing `SECURITY.decision.md` for override justification  

**Next Actions**:  
- Reconstruct security constraint from test changes: `./dx trace --file=tests/security_scanner_test.py --diff`  
- Check for residual decision artifacts: `find . -name '*.decision.*'`  

**Unresolved**:  
Why does `config.security_level` increase break compatibility? (No observable link between config change and RFC)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
