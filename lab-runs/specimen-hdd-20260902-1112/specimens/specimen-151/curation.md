ACCEPT_R1

contrastiveness: high (unchanged flags vs leftover no-step-files after trackSteps vs private cache vs steps in key)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — locations() already in the key while steps() was omitted; leftover HIT skipped the writer
ecosystem: eolang / maven transpile cache
mechanism_family: leftover-transpile-cache, omitted-tracksteps-from-cache-key, diagnostic-flag-on-cache-hit

Packet is the failing world only. Do not assume a root cause.
