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

Discover it by using it on a type, interface, or contract mismatch between two parts of a codebase.

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

        ### Field Report: Exploring the Unfamiliar CLI Tool  

**Situation**: Encountered a type mismatch in a TypeScript codebase between an API response interface (`UserData`) and a frontend component's expected props (`UserProfileProps`).  

**Actions Taken**:  
1. Ran `mismatch scan ./src` to detect contract violations.  
   ```plaintext
   [OUTPUT]  
   Detected 1 contract mismatch:  
   - File: ./src/components/UserProfile.tsx  
     Line 23: Component 'UserProfile' expects 'age: number'  
   - File: ./src/api/userService.ts  
     Line 8: Endpoint 'fetchUser' returns 'age: string'  
   ```  

2. Attempted auto-resolution with `mismatch fix --strategy=coerce ./src/api/userService.ts`:  
   ```plaintext
   [ERROR]  
   Auto-fix failed:  
   Ambiguous conversion path (string→number).  
   Requires manual input.  
   ```  

3. Investigated conversion options using `mismatch explain ./src/api/userService.ts:8.age`:  
   ```plaintext
   [OUTPUT]  
   Property 'age': string → number  
   Available transforms:  
   1. Number(age)        // Coercion (risky for non-numeric strings)  
   2. parseInt(age, 10)  // Safe integer conversion  
   3. Custom mapper       │ Run `mismatch generate-mapper`  
   ```  

4. Generated a custom mapper stub:  
   ```bash
   mismatch generate-mapper --name=ageConverter --input=string --output=number
   ```
   ```typescript
   [GENERATED FILE: ./mappers/ageConverter.ts]  
   export default function ageConverter(input: string): number {  
     // IMPLEMENT: Add conversion logic  
     throw new Error('Not implemented');  
   }  
   ```  

5. Linked the mapper to the mismatch:  
   ```bash
   mismatch attach-mapper ./src/api/userService.ts:8.age --mapper=./mappers/ageConverter.ts
   ```  
   ```plaintext
   [SUCCESS]  
   Applied mapper to:  
   - api/userService.ts:8.age  
   - components/UserProfile.tsx:23.age (inferred)  
   ```  

6. Re-ran validation:  
   ```bash
   mismatch verify --changed
   ```  
   ```plaintext
   [OUTPUT]  
   Contract restored:  
   - All type flows consistent via 'ageConverter'  
   ```  

**Key Observations**:  
- The tool:  
  - Identifies bidirectional contract mismatches (API↔UI)  
  - Generates stubs for custom transformations  
  - Maintains traceability between mismatched points  
- **Limitations**:  
  - Avoids speculative type conversions (requires explicit mapper)  
  - No automatic code modification for ambiguous cases  
  - Mapper files must be manually implemented  

**Next Steps**:  
- Test runtime behavior after implementing `ageConverter` logic  
- Verify propagation to other usage points with `mismatch trace ./mappers/ageConverter.ts`  

---  
**Environment State**:  
- Active mapper binding between `userService.ts` and `UserProfile.tsx`  
- Custom mapper stub requires implementation  
- Tool now monitors `age` type flows project-wide

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
