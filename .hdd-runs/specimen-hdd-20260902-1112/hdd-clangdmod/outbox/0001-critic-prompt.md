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

clangd `IsModuleFileUpToDate` can keep the identity of a **previous C++20 module BMI** after a header included by the module unit was rewritten and the BMI should have been different. `HeaderSearchOptions.ValidateASTInputFilesContent` is set true, but `ASTReader` is constructed without `ValidateASTInputFilesContent=true`. StandardCXXModule input files skip content validation. `canReuse` stays true; leftover previous `getValue()` / header bytes stay current.

On failing_ref `dc4df5da886e09d36577b3302952bc91b5e7e154`:

```
HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
...
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
if (Reader.ReadAST(...) != ASTReader::Success)
  return false;
bool UpToDate = true;
Reader.getModuleManager().visit([&](serialization::ModuleFile &MF) -> bool {
  Reader.visitInputFiles(MF, /*IncludeSystem=*/false, /*Complain=*/false,
      [&](const serialization::InputFile &IF, bool isSystem) {
        if (!IF.getFile() || IF.isOutOfDate())
          UpToDate = false;
      });
  return !UpToDate;
});
return UpToDate;
```

`ASTReader` default skips content validation for StandardCXXModule files unless its own `ValidateASTInputFilesContent` argument is true. HSOpts is not that argument.

Public report (llvm/llvm-project#187653). Module includes `header1.h` (`return 42`); `canReuse` true; rewrite header; leftover previous BMI still reused. In-tree after the repair: ASTReader gets `ValidateASTInputFilesContent=true`; header rewrite is OutOfDate.

Case A — second parse, same header bytes:
  cache identity is current
  not leftover-after-rewrite

Case B — header rewritten, leftover BMI:
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C — rebuild modules / no prior BMI:
  fresh module identity
  not leftover previous BMI

Case D — ValidateASTInputFilesContent on ASTReader (post-repair shape, not on failing_ref):
  new BMI after header rewrite
  not leftover previous module

The developer wants to know which identity case B actually used for the module after the header rewrite: leftover previous-BMI (content validation omitted), current header bytes, or omitted (no module cache).

# OBSERVED

Public llvm/llvm-project#187653 (merged 2026-03-23). Squash `5ef593b75010301528f665ddbe7d2999165b9238` (parent `dc4df5da886e09d36577b3302952bc91b5e7e154`). Local clangd was not performed on this lab host.

PR body: IsModuleFileUpToDate did not properly validate input files for C++20 modules. ASTReader skips StandardCXXModule input validation unless ForceCheckCXX20ModulesInputFiles and ValidateASTInputFilesContent are both set on the reader. Test: header change in a module unit must be detected.

On failing_ref, HSOpts sets the flags but ASTReader is constructed with defaults `{}`. visitInputFiles mtime/out-of-date does not content-hash the header.

Not this packet: specimen-013 bindname last-wins. specimen-075 rustc incremental. specimen-147 CDK truncated mtime.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref dc4df5da886e09d36577b3302952bc91b5e7e154
# clang-tools-extra/clangd/ModulesBuilder.cpp IsModuleFileUpToDate

# public shape:
# leftover C++20 module BMI after header rewrite
# ASTReader constructed without ValidateASTInputFilesContent
# rebuild / reader flag yields a new BMI
```

Source-backed only. Do not execute untrusted checkouts on the host.

llvm/llvm-project
  clang-tools-extra/clangd/ModulesBuilder.cpp

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  clangd C++20 prerequisite module BMI
  leftover BMI after header rewrite

Case A (second parse, same header bytes):
  current cache identity
  not leftover-after-rewrite

Case B (header rewritten, leftover BMI):
  leftover: previous module / previous header bytes
  ASTReader content validation omitted
  canReuse true

Case C (rebuild modules / no prior BMI):
  fresh module identity
  not leftover previous BMI

Case D (ValidateASTInputFilesContent on ASTReader):
  new BMI after header rewrite
  not leftover previous module

Not this packet:
  bindname last-wins (specimen-013)
  rustc incremental fingerprint (specimen-075)

### module_uptodate_failing.cpp

// Reduced excerpt of IsModuleFileUpToDate on failing_ref
// clang-tools-extra/clangd/ModulesBuilder.cpp
// dc4df5da886e09d36577b3302952bc91b5e7e154
// HSOpts sets ValidateASTInputFilesContent; ASTReader is constructed without it.

HSOpts.ForceCheckCXX20ModulesInputFiles = true;
HSOpts.ValidateASTInputFilesContent = true;
ASTReader Reader(PP, *ModCache, /*ASTContext=*/nullptr,
                 PCHOperations.getRawReader(), CodeGenOpts, {});
// leftover previous BMI after header rewrite

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

        Based on the provided material and operating within the constraints of the environment, I'll investigate the identity case B using the available CLI tool. The tool appears to be a code analysis utility capable of examining AST and module behaviors without executing untrusted checkouts.

**Concrete investigation steps:**

1. **Inspect ASTReader construction parameters**  
   ```bash
   cli-tool ast-inspect --function=ASTReader::ASTReader \
                        --param=ValidateASTInputFilesContent \
                        --context=module_uptodate_failing.cpp
   ```
   **Output:**  
   `ValidateASTInputFilesContent=false (default) in ASTReader constructor. No explicit setting detected in call site.`

2. **Check InputFile validation behavior**  
   ```bash
   cli-tool flag-trace --flag=ValidateASTInputFilesContent \
                       --callstack=serialization::InputFile::isOutOfDate \
                       --scenario=StandardCXXModule
   ```
   **Output:**  
   ```
   [InputFile::isOutOfDate]  
   └── Validation path for StandardCXXModule:  
       ├── ValidateASTInputFilesContent? [missing]  
       ├── ForceCheckCXX20ModulesInputFiles? [unused in this context]  
       └── Fallback to mtime-only check  
   ```

3. **Reproduce case B with header rewrite simulation**  
   ```bash
   cli-tool module-simulate --scenario=leftover-bmi \
                            --header-change=content \
                            --validation-level=no-content-hash \
                            --report-identity
   ```
   **Output:**  
   ```
   SIMULATION: Case B (header rewritten, leftover BMI)  
   ├── Module identity source: previous BMI  
   ├── Header validation: mtime-only (no content hash)  
   ├── ASTReader::canReuse: true  
   └── Actual header bytes used: PREVIOUS (cached in BMI)  
   ```

4. **Verify HSOpts vs ASTReader flag propagation**  
   ```bash
   cli-tool flag-flow --start=HeaderSearchOptions.ValidateASTInputFilesContent \
                      --end=ASTReader.ValidateASTInputFilesContent \
                      --code-path=ModulesBuilder.cpp
   ```
   **Output:**  
   `No propagation path found. HeaderSearchOptions settings do not modify ASTReader constructor parameters in this workflow.`

**Key observations:**

1. **Identity resolution for Case B**  
   The module identity originates from the **leftover previous BMI** after header rewrite. The ASTReader uses cached header bytes from the BMI without revalidating content because:
   - `ValidateASTInputFilesContent` isn't passed to ASTReader constructor
   - StandardCXXModule files skip content validation by default
   - `isOutOfDate()` only performs mtime checks

2. **Flag disconnect confirmed**  
   The `HeaderSearchOptions` settings never reach `ASTReader`'s internal validation mechanisms. The environment shows no evidence of:
   - Automatic flag propagation between these components
   - Content hash usage in validation pipeline
   - System header filtering affecting this scenario

3. **Failure mechanism**  
   The combination of leftover BMI + missing content validation causes:
   ```mermaid
   graph LR
   A[Rewritten Header] --> B[Unchanged mtime?]
   B -->|Yes| C[isOutOfDate=false]
   B -->|No| D[isOutOfDate=true]
   C --> E[Reuse previous BMI]
   D --> F[Invalidate BMI]
   ```
   **Actual behavior:** Path C→E occurs because:
   - Header change doesn't invalidate BMI without content hashing
   - Previous header bytes remain active via BMI cache

**Conclusion:**  
Case B uses the **leftover previous BMI identity** containing stale header bytes. The environment shows no evidence of current header bytes being incorporated or module omission. The core failure is the lack of content validation in the ASTReader pipeline despite higher-level flags being set.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
