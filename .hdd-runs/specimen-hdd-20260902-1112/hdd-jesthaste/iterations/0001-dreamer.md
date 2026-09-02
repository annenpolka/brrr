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
