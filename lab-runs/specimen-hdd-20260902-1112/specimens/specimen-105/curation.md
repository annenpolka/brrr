ACCEPT_R1

contrastiveness: high (shared npm specifier leftover vs unshared jsr drop vs npm-only root vs both remain)
reproducibility: source-backed PR + pinned parent/merge; in-tree spec added by the PR; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — jsr.dependencies and specifiers are different identity tables; purge walks npm ids through root_packages then serializes the unfiltered jsr set
ecosystem: deno / lockfile
mechanism_family: leftover-specifier, jsr-deps, workspace-purge

Packet is the failing world only. Do not assume a root cause.
