KNOWN FIX (sealed): microsoft/TypeScript PR 49543 squash df2192697670d2bf8840c1e4fcd51cbf8a13cee9.

failing_ref is squash parent 8ed846c73b5033087eee119ae00511e019f91729.

Incremental file signature was hash(d.ts emit text) only. A d.ts-text-stable change that still changed d.ts diagnostics (public vs protected mixin field) left leftover signature identity in .tsbuildinfo; importers were not rechecked and kept stale TS2445.

PR repair: computeSignatureWithDiagnostics folds d.ts emit diagnostics into the signature (start/length + category + code + message). emitSignature stays the d.ts-text hash when there are no diagnostics. Signature change then rechecks importers.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
