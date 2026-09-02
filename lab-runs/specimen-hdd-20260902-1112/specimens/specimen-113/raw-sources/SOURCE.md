repository: microsoft/TypeScript
issue: https://github.com/microsoft/TypeScript/issues/64025
pr: https://github.com/microsoft/TypeScript/pull/64026
failing_ref (squash parent / PR base): 5739027c9a7df24e27123f453a50c011b37717b6
fixed_ref (squash merge): 13e158b131a6ec523fc6ee76376c8ff1a55451ab
merged_at: 2026-09-01T19:20:39Z
pr_author: Copilot
merged_by: jakebailey
changed_files: tsc/internal/execute/incremental/affectedfileshandler.go, tsc/internal/execute/tsctests/tsc_test.go, tsc/testdata/baselines/reference/tsc/incremental/json-module-diagnostics-are-cleared-after-fixing-the-json-file.js
pr_title: Clear stale incremental diagnostics after JSON module changes
scout_note: not specimen-067/075. Distinct leftover: tsbuildinfo semanticDiagnostics vs JSON source identity. job-0460.
