ACCEPT_R1

contrastiveness: high (unchanged source stage vs leftover RUN --mount after rebuild vs --no-cache vs DidExecute avoid cache)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — mountpoint path and whether the source stage executed this build are different identities; leftover RUN layer stayed current
ecosystem: buildah / layer cache
mechanism_family: leftover-mount-stage, omitted-did-execute, run-mount-from-stage-cache

Packet is the failing world only. Do not assume a root cause.
