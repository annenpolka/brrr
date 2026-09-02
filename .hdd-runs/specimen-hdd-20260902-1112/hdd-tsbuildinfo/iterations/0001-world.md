# Current situation

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
