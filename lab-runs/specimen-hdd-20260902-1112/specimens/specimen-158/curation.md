ACCEPT_R1

contrastiveness: high (unset vs leftover unset after FOO= JOIN vs present FOO=bar vs empty present)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — empty string and unset JOIN to one Windows size-zero identity; two greps cannot replace
ecosystem: vcpkg / Windows getenv
mechanism_family: leftover-empty-vs-unset, getenv-zero-join, windows-empty-env

Packet is the failing world only. Do not assume a root cause.
