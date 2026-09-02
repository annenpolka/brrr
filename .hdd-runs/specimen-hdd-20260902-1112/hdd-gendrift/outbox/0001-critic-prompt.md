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

GitHub Actions job `Tests / Check if generated files are up to date` (`check-generated-files`) fails on main after a generator change landed.

The job log for run 15115778970 includes a diff of `Include/internal/pycore_opcode_metadata.h` inside `_PyOpcode_Deopt`:

```
-    [119] = 119,
-    [120] = 120,
     [121] = 121,
...
-    [211] = 211,
     [212] = 212,
```

The same revision already contains a `// This file is generated by Tools/cases_generator/opcode_metadata_generator.py` header, and `Tools/cases_generator/opcode_metadata_generator.py` was just changed to emit identity rows for opcode numbers missing from `analysis.opmap`.

The developer wants to know which checked-in generated file disagrees with `make regen-all`, and how those numeric identity rows relate to named opcode ids on the same revision.

# OBSERVED

Public python/cpython issue 134236 / PR 134231. Failing world after merge of #128044 (`cc9add695da42defc72e62c5d5389621dac54b2b`, "Mark unknown opcodes as deopting to themselves").

CI job name: `Check if generated files are up to date`.
CI log (issue 134236, actions run 15115778970):

```
Generated files not up to date.
Perhaps you forgot to run make regen-all or build.bat --regen. ;)
```

plus the `_PyOpcode_Deopt` hunk above.

On the failing revision, `generate_deopt_table` in `opcode_metadata_generator.py` does:

1. one named row per `analysis.instructions` (`[inst.name] = deopt`)
2. then, for every `i in range(256)` whose value is **not** in `analysis.opmap.values()`, a numeric row `[i] = i`
3. `assert len(deopts) == 256`

Checked-in `Include/internal/pycore_opcode_metadata.h` on that revision starts `_PyOpcode_Deopt` with numeric keys including 119, 120, and 211.

`Include/opcode_ids.h` on the same revision:

```
#define UNPACK_SEQUENCE                        119
#define YIELD_VALUE                            120
#define UNPACK_SEQUENCE_TWO_TUPLE              211
```

The same generated header also already has named deopt rows later in the table:

```
[UNPACK_SEQUENCE] = UNPACK_SEQUENCE,
[UNPACK_SEQUENCE_TWO_TUPLE] = UNPACK_SEQUENCE,
[YIELD_VALUE] = YIELD_VALUE,
```

`Makefile.pre.in` `regen-opcode-metadata` runs `opcode_metadata_generator.py` against `Python/bytecodes.c` and updates `pycore_opcode_metadata.h`. `regen-all` includes `regen-cases`, which includes `regen-opcode-metadata`.

This packet does not include a local clone; treat the snippets and CI message as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# CI job: check-generated-files
#   name: Check if generated files are up to date
./configure --config-cache --with-pydebug --enable-shared
make -j4 regen-all
make regen-stdlib-module-names regen-sbom regen-unicodedata
git add -u
git status --porcelain
git diff -- Include/internal/pycore_opcode_metadata.h
```

Not executed on this lab host.

python/cpython
  Include/internal/pycore_opcode_metadata.h
  Include/opcode_ids.h
  Python/bytecodes.c
  Tools/cases_generator/opcode_metadata_generator.py
  Makefile.pre.in
  .github/workflows/build.yml

RELEVANT MATERIAL

### ci_check.excerpt.yml

# .github/workflows/build.yml on failing_ref (reduced)

check-generated-files:
  name: 'Check if generated files are up to date'
  runs-on: ubuntu-24.04
  steps:
    - name: Build CPython
      run: |
        make -j4 regen-all
        make regen-stdlib-module-names regen-sbom regen-unicodedata
    - name: Check for changes
      run: |
        git add -u
        changes=$(git status --porcelain)
        if test -n "$changes"; then
          echo "Generated files not up to date."
          echo "Perhaps you forgot to run make regen-all or build.bat --regen. ;)"
          echo "$changes"
          git diff --staged || true
          exit 1
        fi

### deopt_table_failing.h

// This file is generated by Tools/cases_generator/opcode_metadata_generator.py
// from:
//   Python/bytecodes.c
// Do not edit!
//
// Reduced excerpt of _PyOpcode_Deopt on failing_ref
// Include/internal/pycore_opcode_metadata.h

const uint8_t _PyOpcode_Deopt[256] = {
    [119] = 119,
    [120] = 120,
    [121] = 121,
    [122] = 122,
    [123] = 123,
    [124] = 124,
    [125] = 125,
    [126] = 126,
    [127] = 127,
    [211] = 211,
    [212] = 212,
    [213] = 213,
    /* ... named rows later in the same table ... */
    [UNPACK_SEQUENCE] = UNPACK_SEQUENCE,
    [UNPACK_SEQUENCE_LIST] = UNPACK_SEQUENCE,
    [UNPACK_SEQUENCE_TUPLE] = UNPACK_SEQUENCE,
    [UNPACK_SEQUENCE_TWO_TUPLE] = UNPACK_SEQUENCE,
    [YIELD_VALUE] = YIELD_VALUE,
};

### generate_deopt_table.py

# Reduced excerpt of generate_deopt_table on failing_ref
# Tools/cases_generator/opcode_metadata_generator.py

def generate_deopt_table(analysis: Analysis, out: CWriter) -> None:
    out.emit("extern const uint8_t _PyOpcode_Deopt[256];\n")
    out.emit("#ifdef NEED_OPCODE_METADATA\n")
    out.emit("const uint8_t _PyOpcode_Deopt[256] = {\n")
    deopts: list[tuple[str, str]] = []
    for inst in analysis.instructions.values():
        deopt = inst.name
        if inst.family is not None:
            deopt = inst.family.name
        deopts.append((inst.name, deopt))
    defined = set(analysis.opmap.values())
    for i in range(256):
        if i not in defined:
            deopts.append((f'{i}', f'{i}'))

    assert len(deopts) == 256
    assert len(set(x[0] for x in deopts)) == 256
    for name, deopt in sorted(deopts):
        out.emit(f"[{name}] = {deopt},\n")
    out.emit("};\n\n")

### opcode_ids.excerpt.h

/* Include/opcode_ids.h on failing_ref (generated; numbers only). */
#define UNPACK_SEQUENCE                        119
#define YIELD_VALUE                            120
#define UNPACK_SEQUENCE_LIST                   209
#define UNPACK_SEQUENCE_TUPLE                  210
#define UNPACK_SEQUENCE_TWO_TUPLE              211

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
