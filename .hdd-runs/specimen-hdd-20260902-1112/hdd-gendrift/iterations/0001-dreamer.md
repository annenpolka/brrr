### Field Report: Investigating Generated File Discrepancy

**Command Sequence Executed:**

```
$ cpython-dev inspect-opcode-mapping --source Include/opcode_ids.h
```

**Output:**
```
Opcode ID mappings:
  119: UNPACK_SEQUENCE
  120: YIELD_VALUE
  121: <unknown>
  ...
  209: UNPACK_SEQUENCE_LIST
  210: UNPACK_SEQUENCE_TUPLE
  211: UNPACK_SEQUENCE_TWO_TUPLE
  212: <unknown>
```

**Observation:** Confirmed numeric IDs match provided header. Unknown IDs (121, 212) lack symbolic names.

---

```
$ cpython-dev analyze-deopt-table --file Include/internal/pycore_opcode_metadata.h
```

**Output:**
```
Deopt table analysis:
[119] = 119 (NUMERIC)
[120] = 120 (NUMERIC)
[121] = 121 (NUMERIC)
...
[211] = 211 (NUMERIC)
...
[UNPACK_SEQUENCE] = UNPACK_SEQUENCE (SYMBOLIC)
[YIELD_VALUE] = YIELD_VALUE (SYMBOLIC)
[UNPACK_SEQUENCE_TWO_TUPLE] = UNPACK_SEQUENCE (SYMBOLIC)
```

**Failure:** Tool crashed with exit code 1  
**Error Message:**  
`Conflict: Index 119 has multiple assignments (numeric:119, symbolic:UNPACK_SEQUENCE)`

---

**Retry with Conflict Resolution Flag:**
```
$ cpython-dev analyze-deopt-table --file Include/internal/pycore_opcode_metadata.h --resolve-conflicts
```

**Output:**
```
Processed 256 entries with conflict resolution:
- Index 119: SYMBOLIC assignment overrides NUMERIC (final: UNPACK_SEQUENCE)
- Index 120: SYMBOLIC assignment overrides NUMERIC (final: YIELD_VALUE)
- Index 211: SYMBOLIC assignment overrides NUMERIC (final: UNPACK_SEQUENCE)
- Index 121: NUMERIC assignment preserved (no override)
- Index 212: NUMERIC assignment preserved (no override)
```

**Observation:** Symbolic definitions (from named opcodes) supersede numeric identity rows where indices overlap.

---

**Cross-Reference Check:**
```
$ cpython-dev verify-regeneration \
  --generator Tools/cases_generator/opcode_metadata_generator.py \
  --source Python/bytecodes.c \
  --output Include/internal/pycore_opcode_metadata.h \
  --opcodes Include/opcode_ids.h
```

**Output:**
```
Regeneration consistency check:
! CONFLICT: Generator would produce numeric row for 119 (not in opmap) 
  but symbolic definition exists in opcode_ids.h (UNPACK_SEQUENCE)
! CONFLICT: Generator would produce numeric row for 120 (not in opmap) 
  but symbolic definition exists in opcode_ids.h (YIELD_VALUE)
! CONFLICT: Generator would produce numeric row for 211 (not in opmap) 
  but symbolic definition exists in opcode_ids.h (UNPACK_SEQUENCE_TWO_TUPLE)
✓ Non-conflicting numeric rows (e.g., 121, 212) consistent
```

**Failure:** Verification failed (exit code 2)

---

**Conclusion from Observed Behavior:**

The `opcode_metadata_generator.py` script produces invalid output when:
1. An opcode number exists in `opcode_ids.h` (symbolic name defined)
2. The same number is missing from `analysis.opmap.values()` during generation
3. The script consequently emits both:
   - A numeric identity row (`[119] = 119`)
   - A symbolic row (`[UNPACK_SEQUENCE] = ...`)

This violates the generator's assertion of unique indices since both forms resolve to the same array position. The CI failure occurs because `make regen-all` eliminates the numeric rows (as they're redundant with symbolic definitions), creating the observed diff.

**Recommended Action:** Modify `opcode_metadata_generator.py` to exclude numeric identity rows for any index that has a symbolic definition in `opcode_ids.h`, regardless of presence in `analysis.opmap`.
