# Fossil: hdd-pipe

- At: 2026-09-01 22:23:21 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: analyze, transform, generate, and verify source, optionally via pipes
- Nearest existing operation: eslint, jscodeshift, a compiler, jq
- Observable delta: none beyond being pipe-friendly
- Reason: the seed was pipeline use; the artifact is a conventional codegen/lint suite
- Iteration: 1
- Do not send back to R1 with "make this more novel".
