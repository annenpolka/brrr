ACCEPT_R1

contrastiveness: high (GOWORK=off own graph vs workspace-replace mustSelect leftover vs same replace vs go.work override)
reproducibility: source-backed issue+CL + pinned parent/submit SHAs; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — workspace replace identity and per-module replace identity are different objects; continue kept leftover go.mod
ecosystem: go / workspaces
mechanism_family: leftover-workspace-replace, silent-continue, go-work-sync

Packet is the failing world only. Do not assume a root cause.
