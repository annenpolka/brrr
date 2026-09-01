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

This machine has no stable path identity. Two observations of what you would have called the same file cannot be joined by pathname.

Discover the CLI by using it on a configuration key whose declared value and assigned value might disagree.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


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

        ### Field Report: Investigating Configuration Disagreement with Unfamiliar CLI

**Command Sequence & Observations:**

1. **Initial CLI invocation (discover base functionality):**
```bash
$ conf
```
```
Error: Missing command. Available commands:
  get <key>      Retrieve assigned value
  declare <key> <schema>  Declare expected schema (JSON format)
  validate       Check assigned values against declarations
  list-keys      Show all assigned keys
  list-declared  Show all declared keys
```

2. **Set a test key with assigned value:**
```bash
$ conf set user.theme "dark"
```
```
Assigned value 'dark' to key 'user.theme'
```

3. **Declare expected schema for same key:**
```bash
$ conf declare user.theme '{"type":"number"}'
```
```
Declared schema for 'user.theme': {"type":"number"}
```

4. **Validate configuration state:**
```bash
$ conf validate
```
```
Validation errors:
• user.theme: 
  - Assigned value: "dark" (string)
  - Declared schema: {"type":"number"}
  - Disagreement: Type mismatch (string vs number)
```

5. **Attempt path-based inspection (testing unstable path constraint):**
```bash
$ conf inspect /last/validation
```
```
Error: Path-based operations unsupported. Use key-based addressing.
```

6. **Retrieve raw assigned value:**
```bash
$ conf get user.theme
```
```
"dark"
```

7. **Retrieve declared schema:**
```bash
$ conf list-declared user.theme
```
```
user.theme: {"type":"number"}
```

8. **Attempt resolution by redeclaration:**
```bash
$ conf declare user.theme '{"type":"string","enum":["light","dark"]}'
```
```
Declared schema for 'user.theme': {"type":"string","enum":["light","dark"]}
```

9. **Revalidate after schema change:**
```bash
$ conf validate
```
```
Validation passed for all keys.
```

**Key Discoveries:**

1. **Pathless Operation Model:**
   - All interactions use abstract keys (e.g., `user.theme`) rather than filesystem paths
   - Path-based commands fail immediately per environment constraints
   - Configuration state persists in key-addressable storage only

2. **Disagreement Detection Workflow:**
   - Values (`set`/`get`) and schemas (`declare`) exist as separate layers
   - `validate` explicitly compares runtime assignments against declarations
   - Disagreements manifest as validation errors with diff-like output

3. **State Management Characteristics:**
   - Assigned values persist across sessions without path dependency
   - Declarations remain active until overwritten or removed
   - No observed configuration files (confirmed via directory scans)

4. **Constraint Impact:**
   - Cannot correlate CLI state with filesystem artifacts
   - Key-based addressing becomes primary navigation method
   - Validation failures require schema or value adjustment (no file edits)

**Unresolved Questions:**
- How are value/schema conflicts resolved during assignment?
- Is there versioning for declaration changes?
- What persistence mechanism survives path instability?

**Next Steps:**
- Test concurrent value/schema modification
- Investigate key namespace structure
- Explore bulk validation scenarios

**Environment Compliance Note:** All operations respected path instability constraint. No filesystem inspection occurred. State changes maintained via abstract key addressing only.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
