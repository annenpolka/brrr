KNOWN FIX (sealed): microsoft/TypeScript PR 64026 squash 13e158b131a6ec523fc6ee76376c8ff1a55451ab.

failing_ref is squash parent 5739027c9a7df24e27123f453a50c011b37717b6.

JSON modules used empty declaration emit as shape signature, so content changes looked shape-equivalent and leftover semanticDiagnosticsPerFile was replayed.

PR repair: skip dts signature for JSON source files; use file version as shape signature so dependents re-check.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
