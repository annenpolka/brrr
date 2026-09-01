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

Discover it by using it while integrating two branches that both changed overlapping areas.

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

        ### Field Report: Branch Integration Attempt

**Command Executed:**  
`integrate branch-merge --source feature/parser-update --target main`

**Output:**  
```
Merging changes from 'feature/parser-update' into 'main'...  
Conflict detected: 3 overlapping regions  
┌──────────────┬──────────────────────────────┐  
│ File         │ Sections                     │  
├──────────────┼──────────────────────────────┤  
│ src/lexer.js │ Lines 48-52, 89-95, 120-125  │  
│ config.yml   │ Lines 10-14                  │  
│ tests/io.js  │ Lines 201-210                │  
└──────────────┴──────────────────────────────┘  
Enter resolution mode? (Y/n):  
```

**Action Taken:**  
Confirmed entry to resolution mode with `Y`

**New Interface:**  
```
Resolution Dashboard  
────────────────────  
Pending: 3 conflict blocks  
Navigating to first block: src/lexer.js (Lines 48-52)  

[Incoming Changes - feature/parser-update]  
const token = new Token(  
  type: 'IDENTIFIER',  
  value: input.slice(start, pos)  
);  

[Current Branch - main]  
const token = Token.build(  
  type: 'IDENTIFIER',  
  raw: input.slice(start, pos)  
);  

Options:  
1. Accept incoming  
2. Keep current  
3. Edit hybrid  
4. Flag unresolved  
>  
```

**Observation:**  
Tool presents granular conflict blocks rather than whole files. No line numbers displayed in diff views, making location tracking difficult. Attempted to inspect surrounding context:

**Command Executed:**  
`context show src/lexer.js:45-55`

**Output:**  
```
Error: Unrecognized command 'context'.  
Available commands in resolution mode:  
- accept [incoming|current]  
- hybrid-edit  
- flag  
- next  
- prev  
- abort-merge  
```

**Action Taken:**  
Chose hybrid edit option (`3`) for first conflict block. Interface changed to:

```
Hybrid Editor - src/lexer.js  
─────────────────────────────  
const token = [Token.build|new Token](  
  type: 'IDENTIFIER',  
  [raw|value]: input.slice(start, pos)  
);  

Guidance:  
• Use [option1|option2] syntax to choose variants  
• Plain text for common elements  
• Type '!done' to finalize  
>  
```

**Resolution Attempt:**  
Manually edited to:
```
const token = Token.build(  
  type: 'IDENTIFIER',  
  value: input.slice(start, pos)  
);  
```
Entered `!done`

**Output:**  
```
Error: Inconsistent selection pattern  
Detected unmarked choice at:  
  Token.build (current branch)  
  new Token (incoming)  
Required: Explicit [current|incoming] tagging  
```

**Retry:**  
Edited to:
```
const token = [current:Token.build](  
  type: 'IDENTIFIER',  
  [incoming:value]: input.slice(start, pos)  
);  
```
Entered `!done`

**Result:**  
```
Block resolved. Moving to next: config.yml (Lines 10-14)  
```

**New Conflict Block:**  
```
[Incoming Changes]  
cache:  
  max_size: 500MB  
  ttl: 3600  

[Current Branch]  
cache:  
  enabled: true  
  ttl: 7200  
```

**Observation:**  
Structural conflict (divergent keys). Attempted manual resolution:

**Command Executed:**  
`hybrid-edit`

**Edited Content:**  
```
cache:  
  [current:enabled]: true  
  [incoming:max_size]: 500MB  
  ttl: [current:7200|incoming:3600]  
```

**Output:**  
```
Error: Ambiguous ttl selection  
Must choose exactly one:  
- current:7200  
- incoming:3600  
```

**Action Taken:**  
Modified to:
```
cache:  
  enabled: true  
  max_size: 500MB  
  ttl: 7200  
```
Entered `!done`

**Result:**  
```
Resolution accepted. Final block: tests/io.js (Lines 201-210)  
```

**Status:**  
Currently examining test conflict block. Merge process remains active with 1 unresolved section. Tool maintains state between commands without resetting context. Confirmed capability to backtrack:

**Command Executed:**  
`prev`

**Output:**  
```
Returned to config.yml (Lines 10-14)  
Previous resolution preserved.  
```

**Next Steps:**  
Complete final conflict resolution in tests/io.js, then attempt merge finalization. Noted absence of automated conflict resolution - all decisions require manual input.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
