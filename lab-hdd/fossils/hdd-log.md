# Fossil: hdd-log

- At: 2026-09-01 22:08:19 JST
- Decision: KILL
- Classification: NO_SURVIVOR
- Core operation: summarize a compiler log and name a root cause
- Nearest existing operation: lnav, rg, tsc pretty-errors, or reading the compiler's own recursive-type diagnostic
- Observable delta: cross-error linking was asserted, but it depended on inventing source and metrics not present in the log
- Reason: once heuristic understanding and fabricated profiling are removed, nothing beyond ordinary log reading remains in this session
- Iteration: 1
- Do not send back to R1 with "make this more novel".
