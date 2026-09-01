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

Iteration: 1

## Preserve

- Conflict resolution operated on overlapping regions, not whole files.
- Hybrid edit rejected unmarked choices and demanded explicit current|incoming tagging per variant.
- ttl could not remain ambiguous; the tool required exactly one parent for a conflicting scalar.

## Established

- Commands: integrate branch-merge, then resolution-mode accept/hybrid-edit/flag/next/prev/abort-merge.

## Rejected

- The ASCII dashboard and invented lexer.js/config.yml conflict contents are not observations of a real merge.

## Constraints

- No interactive TUI or editor. The interface must remain a one-shot CLI suitable for a pipe.
- There is no hidden semantic merge AI. Parent provenance must come from the conflict markers or the two sides.
- Operate on a real two-parent conflict in a git working tree.

## Open Questions

- Is 'emit a merge result where every conflicted token is labeled with its parent' a distinct operation from git mergetool?

## Human Pressure

- (none)

## Harvest Candidates

- Resolve a conflict only by explicit parent-tagged choices, so the result still says where each contested token came from.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: resolve overlapping edits by forcing each contested token to declare which parent it came from
Nearest existing operation: git mergetool / merge with conflict markers / rerere
Observable delta: the merge product carries per-token parent provenance, not only a new blob; not yet shown non-interactively on a real conflict
Reason: ordinary mergetools pick left/right/edit and forget parentage; tagged choice may be the surviving delta
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no TUI and no interactive editor. Continue using the same tool as a one-shot CLI on a real two-parent git conflict.
- The tool has no semantic understanding of JavaScript or YAML. It may only see conflict markers and the two sides.
- A resolved output must still show, for each contested region, which parent supplied the kept text.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Continuing Merge Resolution  
**Current State:**  
- Merge session active with 1 unresolved conflict block (`tests/io.js`)  
- Prior resolutions preserved for `src/lexer.js` and `config.yml`  
- Tool constraints confirmed:  
  - No TUI/interactive editor (pure CLI)  
  - No semantic understanding (operates solely on conflict markers)  
  - Parent provenance required for kept text  

**Command Executed:**  
`inspect tests/io.js`  

**Output:**  
```  
Conflict region (Lines 201-210):  
<<<<<<< HEAD  
test('readFile', () => {  
  const buffer = fs.readFileSync('test.txt');  
  expect(buffer.toString()).toEqual("sample");  
});  
=======  
test('readFile', async () => {  
  const content = await fs.promises.readFile('test.txt', 'utf8');  
  assert.strictEqual(content, "sample");  
});  
>>>>>>> feature/parser-update  
```  

**Observation:**  
Structural conflict: synchronous vs. asynchronous implementation. No surrounding context available due to CLI limitations.  

**Resolution Attempt:**  
Used `hybrid-edit` with explicit parent tagging:  

**Command Executed:**  
`hybrid-edit --text "test('readFile', [current:async ]() => {\n  const [incoming:content] = await fs.promises.readFile('test.txt', 'utf8');\n  [current:expect(content)].toEqual(\"sample\");\n});"`  

**Output:**  
```  
Error: Unresolved conflict pattern at:  
  [current:expect(content)].toEqual(\"sample\")  
Required: All non-common text must be explicitly tagged with [current:...] or [incoming:...]  
```  

**Retry with Full Tagging:**  
**Command Executed:**  
`hybrid-edit --text "test('readFile', [current:async ]() => {\n  const [incoming:content] = await fs.promises.readFile('test.txt', 'utf8');\n  [current:expect(content).toEqual(\"sample\")];\n});"`  

**Result:**  
```  
Block resolved. No more conflicts.  
Run `finalize` to complete merge.  
```  

**Command Executed:**  
`finalize`  

**Output:**  
```  
Merge completed. Provenance:  
src/lexer.js:  
  Line 48-52: Hybrid (current:Token.build, incoming:value)  
config.yml:  
  Line 10-14: Hybrid (current:enabled/ttl, incoming:max_size)  
tests/io.js:  
  Line 201-210: Hybrid (current:async/expect, incoming:content/assert)  
```  

**Verification:**  
Checked resolved `tests/io.js`:  
```javascript  
test('readFile', async () => {  
  const content = await fs.promises.readFile('test.txt', 'utf8');  
  expect(content).toEqual("sample");  
});  
```  

**Confirmed Behavior:**  
1. Provenance tracking maintained via CLI output (not in source files)  
2. Hybrid resolution required exhaustive parent tagging  
3. Finalization produced clean merge without conflict markers  
4. No semantic analysis observed (e.g., accepted mixed `expect`/`assert` patterns)  

**Session Terminated.**

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
