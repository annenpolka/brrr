ACCEPT_R1

contrastiveness: high (unchanged exclude vs leftover cache after flip vs rmdir vs OPTIONS_AFFECTING_CACHE member)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — option exists on Options but is omitted from OPTIONS_AFFECTING_CACHE so leftover cache stayed current
ecosystem: mypy / incremental cache
mechanism_family: leftover-incremental-cache, omitted-options-affecting-cache, untyped-calls-exclude

Packet is the failing world only. Do not assume a root cause.
