# OBSERVED

Public microsoft/TypeScript#49527 (closed 2022-06-27). PR 49543 squash `df2192697670d2bf8840c1e4fcd51cbf8a13cee9` (parent `8ed846c73b5033087eee119ae00511e019f91729`). Local tsc was not performed on this lab host.

Issue body: with `incremental: true`, changing `public message` to `protected` then back to `public` still reported TS2445 on `js/main.ts`. Setting `incremental: false` made typecheck succeed. The leftover error identity lived in `.tsbuildinfo`. Related discussion: TypeScript#42769.

On failing_ref, `computeSignature` hashes d.ts emit text (minus sourceMappingURL). Emit of a declaration file uses that hash as `info.signature` / `emitSignatures`. d.ts emit diagnostics are not folded into the signature. Importer recheck is gated on signature change.

`computeSignatureWithDiagnostics` (d.ts text + serialized diagnostics) is **not** on the failing revision. It is added by PR 49543.

Not this packet: specimen-067 (mypy identity-loss / generic-substitution). specimen-075 (rustc incremental query identity). specimen-094 (vitest leftover-cache-key).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
