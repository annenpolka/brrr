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
