# Fossil: hdd-history

- At: 2026-09-01 22:15:17 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: show that a pinned dependency commit no longer matches the remote/manifest pointer
- Nearest existing operation: git submodule status, cargo/npm lockfile diff, git diff on a lockfile
- Observable delta: none that requires a new verb
- Reason: capability removal left ordinary pin/lockfile comparison; no untested delta remains that would change this class
- Iteration: 2
- Do not send back to R1 with "make this more novel".
