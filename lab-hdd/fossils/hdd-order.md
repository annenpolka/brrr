# Fossil: hdd-order

- At: 2026-09-01 22:50:37 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: ask whether earlier change A could have caused later observation B
- Nearest existing operation: git show plus grep of a log for identifiers from the diff
- Observable delta: none demonstrated beyond what git+rg already do; the CLI did not automate the link
- Reason: no untested delta remains that would change the class; do not send back to R1
- Iteration: 2
- Do not send back to R1 with "make this more novel".
