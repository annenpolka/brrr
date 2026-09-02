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
