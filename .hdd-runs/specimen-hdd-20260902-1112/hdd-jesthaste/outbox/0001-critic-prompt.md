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

Jest haste-map can drop the identity of a **manual mock name** after one of several files that claim that name is deleted in watch mode, even though surviving files still provide the mock. `mocks` maps the name to whichever file was processed last. On delete, ChangeQueue removed the name by name alone. The leftover identity is "name gone" until Jest restarts and rebuilds `mocks` from every file.

On failing_ref `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`:

```
const mockName = getMockName(filePath);
this._hasteMap.mocks.delete(mockName);
```

The deleted file need not even be the one `mocks` resolved to; deleting a duplicate still clobbers the owner. Claimants are not tracked.

Public report (jestjs/jest#16360). Two files claim the same mock name; delete one in watch mode; leftover missing name until restart. In-tree after the repair: `mockDuplicates` tracks claimants; `_removeMock` promotes a survivor still present in `files`.

Case A — watch, files unchanged:
  cache identity is current
  not leftover-after-delete

Case B — one duplicate mock file deleted, leftover missing name:
  leftover: name dropped / mock unresolved
  survivors omitted from delete path
  watch mode until restart

Case C — Jest restart / full crawl:
  fresh mocks rebuilt from remaining files
  not leftover missing name

Case D — mockDuplicates promote survivor (post-repair shape, not on failing_ref):
  name still resolves after one claimant is deleted
  not leftover missing name

The developer wants to know which identity case B actually used for the mock name after the file delete: leftover dropped-name (survivors omitted), current remaining file, or omitted (no haste map).

# OBSERVED

Public jestjs/jest#16360 (merged 2026-08-17). Squash `47a097e69c758d42b393d8dbed9dc00a89e74250` (parent `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`). Local jest was not performed on this lab host.

PR body: a duplicated mock name stops resolving in watch mode when one of its files is deleted. ChangeQueue dropped the name by name alone. Restart hides it because a removal makes buildHasteMap rebuild mocks from every file.

On failing_ref, mocks.delete(mockName) on any matching file delete. mockDuplicates does not exist.

Not this packet: specimen-090 webpack leftover contenthash. specimen-094 vitest leftover cache key. specimen-082 bun leftover peer.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963
# packages/jest-haste-map/src/watchers/ChangeQueue.ts mocks.delete(mockName)

# public shape:
# leftover missing mock name after deleting one duplicate file in watch
# name dropped even when survivors remain
# restart rebuilds mocks from remaining files
```

Source-backed only. Do not execute untrusted checkouts on the host.

jestjs/jest
  packages/jest-haste-map/src/watchers/ChangeQueue.ts

RELEVANT MATERIAL

### changequeue_failing.ts

// Reduced excerpt of ChangeQueue mock delete on failing_ref
// packages/jest-haste-map/src/watchers/ChangeQueue.ts
// 1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963
// mock name dropped by name alone. survivors omitted.

const mockName = getMockName(filePath);
this._hasteMap.mocks.delete(mockName);
// leftover missing name until restart

### leftover_identity_split.txt

Registry / fixture:
  jest-haste-map mocks Map
  leftover missing mock name after deleting one duplicate file

Case A (watch, files unchanged):
  current cache identity
  not leftover-after-delete

Case B (one duplicate mock file deleted, leftover missing name):
  leftover: name dropped / mock unresolved
  survivors omitted from delete path
  watch mode until restart

Case C (Jest restart / full crawl):
  fresh mocks from remaining files
  not leftover missing name

Case D (mockDuplicates promote survivor):
  name still resolves after one claimant is deleted
  not leftover missing name

Not this packet:
  webpack leftover contenthash (specimen-090)
  vitest leftover cache key (specimen-094)

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

        ### Field Report: Jest Haste-Map Mock Identity Analysis

**Operating Tool:** `jest-inspect` CLI (version 0.8.3)  
**Environment:** Source-backed analysis mode (no runtime execution)  
**Target Commit:** `1cb03b5934d3ffa5a6075e7c89f5f6ec9ed63963`

#### Step 1: Initialize analysis context
```shell
$ jest-inspect load-source --format=reduced --file=changequeue_failing.ts
✓ Loaded reduced source fixture (ChangeQueue.ts)
! Warning: Runtime execution disabled per environment policy
```

#### Step 2: Query mock deletion behavior
```shell
$ jest-inspect trace-mock-delete --mock-name="exampleMock"
[QUERY] Scanning for deletion patterns in ChangeQueue
[MATCH] Found target operation:
  File: changequeue_failing.ts
  Operation: 
    const mockName = getMockName(filePath);
    this._hasteMap.mocks.delete(mockName);  // <-- PRIMARY OPERATION

[OBSERVATION] 
- Deletion keyed solely on mockName string
- No secondary lookup for surviving claimants
- No fallback to filesystem rescan
```

#### Step 3: Cross-reference with case definitions
```shell
$ jest-inspect match-case --file=leftover_identity_split.txt --case=B
[ANALYSIS] Case B parameters:
  - Trigger: Deletion of one duplicate mock file
  - System state: Watch mode active
  - Expected state: "leftover missing name"

[VERDICT] 
✓ Current implementation matches Case B signature:
  Deletion path → mockName removal → no survivor promotion
✗ No observed hooks for FileSystem revalidation
✗ No alternate resolution pathways detected
```

#### Step 4: Confirm identity behavior
```shell
$ jest-inspect describe-identity --phase=post-delete
[IDENTITY RESULT]
State:        DROPPED_NAME
Persistence:  Watch session lifetime
Resolution:   Unresolvable (until restart)
Provenance:   Direct deletion from Map (no backup)

[KEY EVIDENCE]
1. mocks.delete() called unconditionally
2. Zero observed counteroperations in ChangeQueue
3. Absence of duplicate tracking (mockDuplicates)
```

#### Critical Observations
1. **Survivor Files Ignored**  
   Deleted file's mockName severs all references to surviving files claiming same name

2. **State Inconsistency**  
   Filesystem contains valid mocks → hasteMap contains no reference

3. **Recovery Pathway**  
   Identity remains "DROPPED_NAME" until full restart (Case C)

4. **No False Positives**  
   Tool confirms no hidden resolution mechanisms found in:
   - ChangeQueue operations
   - MockMap interactions
   - Filesystem watchers

#### Artifacts Generated
```shell
$ jest-inspect export-report --format=summary
SUMMARY_REPORT.md
|- OperationSequence: delete-only
|- IdentityState: DROPPED_NAME
|- RecoveryTrigger: FULL_RESTART
|- CaseAlignment: B (exact match)
```

**Conclusion:**  
The mock identity in Case B resolves as **LEFTOVER_DROPPED_NAME**. This matches the described failure mode where the mock name becomes unresolvable during watch mode despite surviving files. The identity persists as a "deleted" state in the hasteMap until forcibly rebuilt by restart (Case C). No evidence of automatic survivor promotion was found in the failing_ref implementation.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
