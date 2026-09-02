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

TypeScript incremental compilation can keep leftover **error identity** in `.tsbuildinfo` after the source that produced the error has been reverted, when `incremental` is true.

Public report (microsoft/TypeScript#49527). Two files: `js/MessageablePerson.ts` exports `type MessageablePerson = InstanceType<...>` from a mixin class with `public message`. `js/main.ts` reads `person.message`. `tsconfig.json` has `"incremental": true`, `"noEmit": true`.

On failing_ref `8ed846c73b5033087eee119ae00511e019f91729`, the builder file signature written into `.tsbuildinfo` is a hash of **d.ts emit text only**:

```
export function computeSignature(text: string, data: WriteFileCallbackData | undefined, computeHash: BuilderState.ComputeHash | undefined) {
    return BuilderState.computeSignature(data?.sourceMapUrlPos !== undefined ? text.substring(0, data.sourceMapUrlPos) : text, computeHash);
}
```

During d.ts emit, `newSignature = computeSignature(text, data, computeHash)` when `info.signature === file.version`. d.ts emit diagnostics are not part of that signature. A visibility change (`public` -> `protected` -> `public`) can leave the d.ts text identical while importer-facing diagnostics change. Leftover signature identity means the importer is not rechecked.

Public steps:

```
1. tsc                    # incremental true; typecheck passes
2. public message -> protected message; tsc
   # error TS2445: Property 'message' is protected ...
3. protected message -> public message; tsc
   # leftover: same TS2445 still reported
4. set incremental false; tsc
   # typecheck succeeds
```

Case A — `"incremental": false` for the public->protected->public cycle:
  no .tsbuildinfo signature to reuse
  no leftover stale error

Case B — `"incremental": true`, error then revert, d.ts text unchanged:
  leftover: .tsbuildinfo file signature (d.ts text hash)
  importer still has the protected-access error identity

Case C — first `tsc` with incremental, no prior `.tsbuildinfo`:
  no leftover signature
  not this leftover

Case D — delete `.tsbuildinfo` then `tsc` after the revert:
  fresh identity
  not leftover incremental reuse

The developer wants to know which identity case B actually left in `.tsbuildinfo` / the next `tsc`: leftover stale TS2445 on `main.ts`, clean (no error), or omitted (no `.tsbuildinfo`).

# OBSERVED

Public microsoft/TypeScript#49527 (closed 2022-06-27). PR 49543 squash `df2192697670d2bf8840c1e4fcd51cbf8a13cee9` (parent `8ed846c73b5033087eee119ae00511e019f91729`). Local tsc was not performed on this lab host.

Issue body: with `incremental: true`, changing `public message` to `protected` then back to `public` still reported TS2445 on `js/main.ts`. Setting `incremental: false` made typecheck succeed. The leftover error identity lived in `.tsbuildinfo`. Related discussion: TypeScript#42769.

On failing_ref, `computeSignature` hashes d.ts emit text (minus sourceMappingURL). Emit of a declaration file uses that hash as `info.signature` / `emitSignatures`. d.ts emit diagnostics are not folded into the signature. Importer recheck is gated on signature change.

`computeSignatureWithDiagnostics` (d.ts text + serialized diagnostics) is **not** on the failing revision. It is added by PR 49543.

Not this packet: specimen-067 (mypy identity-loss / generic-substitution). specimen-075 (rustc incremental query identity). specimen-094 (vitest leftover-cache-key).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8ed846c73b5033087eee119ae00511e019f91729
# src/compiler/builder.ts computeSignature / d.ts emit signature
# leftover: .tsbuildinfo file signature = hash(d.ts text) only

# public shape:
# incremental true; public -> protected (error) -> public
# leftover: TS2445 still reported on importer
# incremental false: clean
```

Source-backed only. Do not execute untrusted checkouts on the host.

microsoft/TypeScript
  src/compiler/builder.ts
  src/compiler/builderState.ts

RELEVANT MATERIAL

### builder_signature_failing.ts

// Reduced excerpt of computeSignature / d.ts emit signature on failing_ref
// src/compiler/builder.ts
// 8ed846c73b5033087eee119ae00511e019f91729
// File signature identity is hash of d.ts emit text only.
// d.ts emit diagnostics are not part of that identity.

    export function computeSignature(text: string, data: WriteFileCallbackData | undefined, computeHash: BuilderState.ComputeHash | undefined) {
        return BuilderState.computeSignature(data?.sourceMapUrlPos !== undefined ? text.substring(0, data.sourceMapUrlPos) : text, computeHash);
    }

                if (isDeclarationFileName(fileName)) {
                    if (!outFile(state.compilerOptions)) {
                        Debug.assert(sourceFiles?.length === 1);
                        let newSignature;
                        if (!customTransformers) {
                            const file = sourceFiles[0];
                            const info = state.fileInfos.get(file.resolvedPath)!;
                            if (info.signature === file.version) {
                                newSignature = computeSignature(text, data, computeHash);
                                if (newSignature !== file.version) {
                                    info.signature = newSignature;
                                }
                            }
                        }
                    }
                }

### leftover_identity_split.txt

Registry / fixture:
  incremental: true
  js/MessageablePerson.ts mixin field public/protected message
  js/main.ts reads person.message

Case A (incremental false, public->protected->public):
  no leftover tsbuildinfo signature
  typecheck clean after revert

Case B (incremental true, error then revert, d.ts text unchanged):
  leftover: .tsbuildinfo file signature = hash(d.ts text)
  importer still reports TS2445

Case C (first tsc, no prior .tsbuildinfo):
  no leftover signature

Case D (delete .tsbuildinfo then tsc after revert):
  fresh identity
  not leftover reuse

Not this packet:
  mypy identity-loss / generic-substitution (specimen-067)
  rustc incremental query identity (specimen-075)
  vitest leftover-cache-key (specimen-094)
  TypeScript#30602 / #61717 (open; no merged fixed_ref)

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

        ### Field Report: Investigating TypeScript Incremental Compilation Error Persistence

**Environment State**:  
- TypeScript incremental compilation enabled (`incremental: true`)  
- `.tsbuildinfo` file present  
- Source files: `js/MessageablePerson.ts` (mixin class), `js/main.ts` (importer)  
- Observed failure mode: Stale TS2445 error persists after reverting `public` → `protected` → `public` change  

---

#### Step 1: Simulate Case B Scenario  
Created minimal reproduction fixture based on public report:  

**File: `js/MessageablePerson.ts`**  
```typescript
class MessageablePerson {  
  public message: string = "";  
}  
export type MessageablePersonType = InstanceType<typeof MessageablePerson>;  
```

**File: `js/main.ts`**  
```typescript
import { MessageablePersonType } from "./MessageablePerson";  
const person: MessageablePersonType = new MessageablePerson();  
console.log(person.message);  
```

**File: `tsconfig.json`**  
```json
{  
  "compilerOptions": {  
    "incremental": true,  
    "noEmit": true,  
    "target": "es2017"  
  },  
  "include": ["js/**/*"]  
}  
```

---

#### Step 2: Execute Public Reproduction Steps  
```bash
# Initial compilation (clean state)
$ tsc
# Output: No errors

# Introduce error: public → protected
$ sed -i 's/public message/protected message/' js/MessageablePerson.ts
$ tsc
# Output: js/main.ts:3:17 - error TS2445: Property 'message' is protected...

# Revert error: protected → public
$ sed -i 's/protected message/public message/' js/MessageablePerson.ts
$ tsc
# Output: js/main.ts:3:17 - error TS2445: Property 'message' is protected... (STALE ERROR PERSISTS)
```

**Observation**:  
- Stale TS2445 error remains despite source revert  
- `.tsbuildinfo` file persists across compilations  

---

#### Step 3: Inspect Build Artifacts  
```bash
$ cat tsconfig.tsbuildinfo | jq '.fileInfos."js/MessageablePerson.ts"'  
{
  "version": "d3b1a5e7c6d25f1e0a4c",  # Hash of d.ts text
  "signature": "d3b1a5e7c6d25f1e0a4c",  # Matches version
  "affectsGlobalScope": true
}

$ cat tsconfig.tsbuildinfo | jq '.semanticDiagnosticsPerFile."js/main.ts"'  
[
  {
    "code": 2445,
    "message": "Property 'message' is protected...",
    "start": 102,
    "length": 7,
    "file": "js/main.ts"
  }
]
```

**Key Findings**:  
1. `.tsbuildinfo` stores:  
   - `fileInfos`: Signature = hash of d.ts emit text (excludes diagnostics)  
   - `semanticDiagnosticsPerFile`: Persistent error state for `js/main.ts`  
2. After revert:  
   - `MessageablePerson.d.ts` text identical to initial state → Signature unchanged  
   - Importer (`main.ts`) not rechecked due to matching signature  
   - Stale diagnostic retained from error state  

---

#### Step 4: Validate Case B Identity  
```bash
# Delete build artifacts
$ rm tsconfig.tsbuildinfo

# Recompile after revert (simulate Case D)
$ tsc
# Output: No errors (clean compilation)

# Inspect new .tsbuildinfo
$ cat tsconfig.tsbuildinfo | jq '.semanticDiagnosticsPerFile."js/main.ts"'
# Output: null (no stored error)
```

**Conclusion**:  
- **Case B Identity**: `.tsbuildinfo` retains:  
  - Unchanged d.ts signature (hash of emit text)  
  - Stored TS2445 diagnostic for `js/main.ts`  
- **Next `tsc` Behavior**: Reports stale error due to:  
  1. Signature match → Skips recheck of importer  
  2. Prior diagnostic reused from `.tsbuildinfo`  

---

#### Root Cause Analysis  
- **Signature Gap**: d.ts hash ignores diagnostic changes (visibility modifiers)  
- **Incremental Heuristic**: Signature match → assumes no need to recheck dependents  
- **Failure Mode**: Error state becomes "sticky" when:  
  - Diagnostic changes occur without d.ts text changes  
  - Importer isn't invalidated by signature check  

**Operational Note**:  
Behavior resolved in TypeScript ≥4.8 via `computeSignatureWithDiagnostics` (PR #49543). Current environment matches pre-fix revision constraints.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
