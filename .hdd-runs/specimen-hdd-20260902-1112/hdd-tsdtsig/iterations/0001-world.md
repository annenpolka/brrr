# Current situation

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
