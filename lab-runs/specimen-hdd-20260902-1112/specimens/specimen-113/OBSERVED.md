# OBSERVED

Public microsoft/TypeScript#64025 (closed 2026-09-01). PR 64026 squash `13e158b131a6ec523fc6ee76376c8ff1a55451ab` (parent `5739027c9a7df24e27123f453a50c011b37717b6`). Local tsc was not performed on this lab host.

Issue body: JSON change that *introduces* the error is detected on a warm run; only clearing is broken. 5.9.3 clears; 7.0.2 / 7.1.0-dev keep leftover TS2741 until tsbuildinfo is deleted.

On failing_ref, JSON modules used empty declaration emit as shape signature. Content-hash in fileInfos updates; dependents' semanticDiagnosticsPerFile is replayed.

Using file version as JSON shape signature is **not** on the failing revision. It is added by PR 64026 (`!ast.IsJsonSourceFile(file)` before computing dts signature).

Not this packet: specimen-067 (mypy leftover). specimen-075 (rust leftover). microsoft/TypeScript#30602 (deleted js not recreated; still open). #59851 (tsbuildinfo unportable paths; still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
