# Fossil: hdd-type

- At: 2026-09-01 22:15:17 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: report a type field that does not match between two files and offer a conversion stub
- Nearest existing operation: tsc / mypy / an LSP quick-fix
- Observable delta: stub file generation; not a new question
- Reason: the compiler already exposes the two-ended mismatch
- Iteration: 1
- Do not send back to R1 with "make this more novel".
