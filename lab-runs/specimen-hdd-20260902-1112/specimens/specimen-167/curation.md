ACCEPT_R1

contrastiveness: high (same-envs current vs leftover after env change vs new process vs envs-keyed)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — vars-only key JOINs two different envs maps; two greps cannot replace
ecosystem: swc / optimizer globals
mechanism_family: leftover-optimizer-env, omitted-envs-cache-key, process-wide-dashmap

Packet is the failing world only. Do not assume a root cause.
