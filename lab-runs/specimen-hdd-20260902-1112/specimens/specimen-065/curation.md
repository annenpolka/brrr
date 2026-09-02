ACCEPT_R1

contrastiveness: high (cgroup v1 remaps via inspect; cgroup v2 pretends to be the host; mountinfo still names the container id)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — “am I in Docker?” is answered from a proc file that changed shape under cgroup v2, so bind-mount rewrite silently does not happen
ecosystem: python / pre-commit
mechanism_family: cgroup-v2, docker-in-docker, false-host

Packet is the failing world only. Do not assume a root cause.
