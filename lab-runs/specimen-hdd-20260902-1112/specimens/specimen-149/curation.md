ACCEPT_R1

contrastiveness: high (user-env match vs leftover image default after drop vs FOO= empty vs keepEmpty unset)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — listed-without-equals, empty string, omitted, and unset-in-container are different identities; leftover image default stayed current
ecosystem: compose / environment resolve
mechanism_family: leftover-empty-vs-unset, listed-without-equals-dropped, leftover-image-env-default

Packet is the failing world only. Do not assume a root cause.
