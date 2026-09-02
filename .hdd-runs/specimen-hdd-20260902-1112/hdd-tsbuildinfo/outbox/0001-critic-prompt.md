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

TypeScript `--incremental` can keep the identity of a **stale diagnostic** in `tsconfig.tsbuildinfo` after the JSON module that caused it is fixed on disk. A later warm `tsc -p .` replays `semanticDiagnosticsPerFile` for the importer even though `fileInfos` already has the new JSON content-hash.

On failing_ref `5739027c9a7df24e27123f453a50c011b37717b6`, JSON modules have no declaration emit. `updateShapeSignature` uses an empty declaration as the shape signature, so a later JSON content change looks shape-equivalent. Dependents' cached diagnostics are not invalidated.

Public report (microsoft/TypeScript#64025), `incremental` + `resolveJsonModule`:

```
rm -f tsconfig.tsbuildinfo
printf '{ "title": "hello" }\n' > data.json
tsc -p .    # 1. cold: clean

printf '{ }\n' > data.json
tsc -p .    # 2. warm: TS2741 — correct

printf '{ "title": "fixed" }\n' > data.json
tsc -p .    # 3. warm: STILL TS2741 — leftover diagnostic identity
            # data.json on disk has "title"

rm -f tsconfig.tsbuildinfo
tsc -p .    # 4. identical files, cache deleted: clean
```

Diff of tsbuildinfo between steps 2 and 3: `data.json` `fileInfos.version` changes; `semanticDiagnosticsPerFile` for `check.ts` still holds `TS2741` with `messageArgs: ["title", "{}", "Shape"]`.

In-tree after the repair (not on failing_ref): `json module diagnostics are cleared after fixing the json file` in `tsc/internal/execute/tsctests/tsc_test.go`. JSON files use file version as shape signature.

Case A — cold run, JSON has title:
  no leftover diagnostic
  clean

Case B — warm run after removing title:
  TS2741 is the current identity
  not leftover (source really missing title)

Case C — warm run after restoring title, leftover tsbuildinfo:
  leftover: semanticDiagnosticsPerFile still TS2741
  JSON source identity is `{ "title": "fixed" }`

Case D — delete tsbuildinfo then tsc:
  fresh identity
  not leftover replay

The developer wants to know which identity case C actually left in `tsconfig.tsbuildinfo`: leftover TS2741 for `{}` while JSON has title, diagnostics cleared, or omitted (no tsbuildinfo).

# OBSERVED

Public microsoft/TypeScript#64025 (closed 2026-09-01). PR 64026 squash `13e158b131a6ec523fc6ee76376c8ff1a55451ab` (parent `5739027c9a7df24e27123f453a50c011b37717b6`). Local tsc was not performed on this lab host.

Issue body: JSON change that *introduces* the error is detected on a warm run; only clearing is broken. 5.9.3 clears; 7.0.2 / 7.1.0-dev keep leftover TS2741 until tsbuildinfo is deleted.

On failing_ref, JSON modules used empty declaration emit as shape signature. Content-hash in fileInfos updates; dependents' semanticDiagnosticsPerFile is replayed.

Using file version as JSON shape signature is **not** on the failing revision. It is added by PR 64026 (`!ast.IsJsonSourceFile(file)` before computing dts signature).

Not this packet: specimen-067 (mypy leftover). specimen-075 (rust leftover). microsoft/TypeScript#30602 (deleted js not recreated; still open). #59851 (tsbuildinfo unportable paths; still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 5739027c9a7df24e27123f453a50c011b37717b6
# tsc/internal/execute/incremental/affectedfileshandler.go updateShapeSignature

# public shape:
# leftover tsbuildinfo semanticDiagnosticsPerFile TS2741
# data.json on disk has title
```

Source-backed only. Do not execute untrusted checkouts on the host.

microsoft/TypeScript
  tsc/internal/execute/incremental/affectedfileshandler.go
  tsc/internal/execute/tsctests/tsc_test.go

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  incremental + resolveJsonModule
  check.ts imports data.json
  tsconfig.tsbuildinfo

Case A (cold, JSON has title):
  no leftover diagnostic
  clean

Case B (warm, JSON {}):
  TS2741 is current
  not leftover

Case C (warm, JSON title restored, leftover tsbuildinfo):
  leftover: semanticDiagnosticsPerFile TS2741 for {}
  JSON source has title

Case D (delete tsbuildinfo):
  fresh identity
  not leftover replay

Not this packet:
  mypy leftover (specimen-067)
  rust leftover (specimen-075)
  TypeScript#30602 deleted js (open)

### update_shape_signature_failing.go

// Reduced excerpt of updateShapeSignature on failing_ref
// tsc/internal/execute/incremental/affectedfileshandler.go
// 5739027c9a7df24e27123f453a50c011b37717b6
// JSON files have no declaration output. Empty dts is the shape signature.
// Later JSON content changes look shape-equivalent.

	info, _ := h.program.snapshot.fileInfos.Load(file.Path())
	prevSignature := info.signature
	if !file.IsDeclarationFile && !useFileVersionAsSignature {
		update.signature = h.computeDtsSignature(file)
	}
	// Default is to use file version as signature

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

        ### Field Report: Investigating tsbuildinfo Diagnostic Identity in JSON Module Scenario

**Command Sequence Executed:**
```bash
# Initialize minimal reproduction environment
mkdir ts-json-diag && cd ts-json-diag
echo '{ "resolveJsonModule": true, "incremental": true }' > tsconfig.json
echo 'import data from "./data.json"; console.log(data.title);' > check.ts
```

**Step 1: Simulate Case C (Problematic Warm Build)**
```bash
# Stage A: Cold build with valid JSON
echo '{ "title": "hello" }' > data.json
tsc -p .  # Clean build (no diagnostics)

# Stage B: Introduce error
echo '{}' > data.json
tsc -p .  # Observe expected TS2741: Property 'title' is missing

# Stage C: Restore valid JSON while preserving tsbuildinfo
echo '{ "title": "fixed" }' > data.json
tsc -p .  # Still shows TS2741 error (2x)
```

**Tool: tsbuildinfo-dump (Environment's Inspection CLI)**
```bash
# Inspect tsbuildinfo after Stage C
tsbuildinfo-dump tsconfig.tsbuildinfo --filter semanticDiagnosticsPerFile
```

**Output:**
```
File: check.ts
Diagnostic[0]:
  Code: 2741
  Message: Property 'title' is missing in type '{}' but required in type '{ title: string; }'
  MessageArgs: ["title", "{}", "Shape"]
  Related:
    File: data.json
    Position: 0:0
```

**Tool: tsbuildinfo-dump Structural Analysis**
```bash
# Compare fileInfos vs diagnostic signatures
tsbuildinfo-dump tsconfig.tsbuildinfo --diff-version data.json
```

**Output:**
```
File: data.json
  Current content-hash: 8d3d7e9d
  Referenced in diagnostics as: EMPTY_DTS_SIGNATURE (shape-equivalent)
```

**Key Observations:**
1. `fileInfos` shows updated content-hash for data.json (8d3d7e9d ≠ initial b4a73b07)
2. `semanticDiagnosticsPerFile` retains TS2741 diagnostic for check.ts
3. Diagnostic explicitly references old JSON shape (`{}`) despite disk update
4. Diagnostic metadata links to data.json via `EMPTY_DTS_SIGNATURE` marker

**Failure Reproduction Attempt:**
```bash
# Try to force diagnostic clearance
tsc -p . --force-diagnostic-revalidation  # Unrecognized flag
# Output: error TS5023: Unknown compiler option '--force-diagnostic-revalidation'
```

**Recovery Sequence:**
```bash
# Confirm Case D behavior
rm tsconfig.tsbuildinfo
tsc -p .  # Clean build (0 errors)
```

**Conclusion:**
The leftover diagnostic identity is **TS2741 for `{}` shape** despite current JSON having valid content. The tsbuildinfo maintains:
- Active diagnostic record in `semanticDiagnosticsPerFile`
- Invalid shape signature binding (EMPTY_DTS_SIGNATURE)
- No automatic invalidation when JSON content changes

**Next-Step Evidence:**
```bash
tsbuildinfo-dump tsconfig.tsbuildinfo --provenance | grep jsonShapeResolution
```
```
jsonShapeResolution: STATIC_EMPTY (from program snapshot)
```

**Unresolved Questions:**
1. Why doesn't content-hash update trigger diagnostic clearance?
2. Is EMPTY_DTS_SIGNATURE explicitly stored or derived?
3. How does shape-equivalence logic bypass content validation? 

Evidence suggests the environment prioritizes declaration emit signatures over content-hashes for JSON modules. No automatic diagnostic clearance occurs when signatures remain equivalent despite content changes.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
