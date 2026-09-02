ACCEPT_R1

contrastiveness: high (uv sources path already git+subdir vs Poetry path leftover directory vs path outside fetch_root vs git root itself)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — lock source identity (directory vs git) is a named join; leftover absolute checkout path is not portable while the live bytes are the git tree
ecosystem: uv / git sources / poetry path
mechanism_family: leftover-directory-in-git, omitted-git-member-on-metadata23, machine-specific-lock-source

Packet is the failing world only. Do not assume a root cause.
