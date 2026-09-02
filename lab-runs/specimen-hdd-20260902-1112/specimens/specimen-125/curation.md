ACCEPT_R1

contrastiveness: high (no-extra sync vs leftover unconditional after extra vs markers kept vs wipe lock)
reproducibility: source-backed issue+PR + pinned parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — extras-marker identity and lock production identity are different objects; leftover true-marker blocked extra-gated isolation
ecosystem: uv / python lock
mechanism_family: leftover-extras-marker, omitted-from-lock, simplified-to-true

Packet is the failing world only. Do not assume a root cause.
