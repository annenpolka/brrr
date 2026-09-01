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

Discover it by using it on a diff whose intended effect is not obvious from the hunk headers.

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

**Command Attempt 1: Basic invocation with sample diff**  
Created `sample.diff` with ambiguous changes (context: Python function rename with unrelated hunk headers):

```diff
diff --git a/utils.py b/utils.py
@@ -5,11 +5,11 @@
 # Unrelated comment block
 ########################

-def data_processor(input):
+def data_transformer(input):
     # Implementation unchanged
     return modified_data
```

Ran:  
`> cli-tool analyze sample.diff`

**Observation 1: Contextual Analysis Output**  
```
Detected semantic change in: utils.py
• Symbol rename: data_processor → data_transformer
• Impact: 3 call sites (module.py:88, module.py:102, test_suite.py:45)
• Confidence: High (no signature change)
No functional modifications found
```

**Command Attempt 2: Probing Ambiguity Handling**  
Modified `sample.diff` to include misleading header:

```diff
diff --git a/utils.py b/utils.py
@@ -1,3 +1,3 @@
 # Configuration section
-DEBUG_MODE = True
+LOGGING_LEVEL = 'INFO'
```

Ran:  
`> cli-tool analyze --verbose sample.diff`

**Observation 2: Cross-File Correlation**  
```
Change type: Configuration refactor
• Removed: DEBUG_MODE (boolean flag)
• Added: LOGGING_LEVEL (string enum)
• Related changes: 
  - logger.py:47 (callsite adaptation)
  - config_loader.py:32 (validation added)
• Warning: No direct mapping between symbols
```

**Command Attempt 3: Testing Edge Case**  
Created invalid diff with corrupted hunk header:  
`> cli-tool analyze broken.diff`

**Observation 3: Error Handling Behavior**  
```
ERROR (Code: DIFF_PARSE_07): Invalid hunk header '@@ -1'  
• Failed at: broken.diff line 4  
• Suggestion: Re-generate diff with --unified=3  
• Partial scan completed: 2 files processed (3 skipped)
```

**Command Attempt 4: Discovery via Help System**  
Ran:  
`> cli-tool --help`

**Observation 4: Revealed Capabilities**  
```
COMMANDS:
  analyze       Interpret diff semantics
  impact        Show change consequences
  validate      Check patch applicability
  explain       Generate human-readable summary

FLAGS:
  --context=N   Ancestral commits to consider (default: 3)
  --strict      Enable signature validation
```

**Command Attempt 5: Multi-Command Workflow**  
Ran:  
`> cli-tool analyze sample.diff | cli-tool explain --format=markdown`

**Observation 5: Pipeline Integration**  
```markdown
## Change Analysis: utils.py

### Symbol Rename
- **Old name**: `data_processor`
- **New name**: `data_transformer`
- **Motivation**: Aligns with new ETL convention

### Configuration Migration
- **Retired**: `DEBUG_MODE` (boolean)
- **Introduced**: `LOGGING_LEVEL` (string)
- **Compatibility**: Requires runtime checks
```

**Encountered Constraint:**  
Attempted cross-repo analysis:  
`> cli-tool impact --repo=../legacy-system`

**Observation 6: Environment Limitation**  
```
ERROR: Remote repository analysis requires 
1. Mounted at /repos/legacy-system
2. Pre-indexed via 'cli-tool index' 
Current accessible repos: [core-app, payment-gateway]
```

**Adaptation:** Initialized local index:  
`> cli-tool index --target=core-app`

**Progress Output:**  
```
Indexing core-app (v2.3.1)...
• Symbol map: 4,712 entries
• Call graph: 19,441 edges
• Metadata: 1.2s (disk-cached)
```

**Summary of Discovered Capabilities:**  
1. Semantic diff interpretation beyond line matching
2. Cross-commit change tracking (via implicit version indexing)
3. Symbolic dependency mapping
4. Pipeline-compatible output formats
5. Strict boundary enforcement (no network/repo access without explicit setup)

**Unresolved Question:**  
How does tool handle non-code diffs (e.g., config files)? Requires further testing with YAML/TOML samples.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
