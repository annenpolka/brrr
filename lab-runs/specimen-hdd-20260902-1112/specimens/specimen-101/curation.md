ACCEPT_R1

contrastiveness: high (https/ssh WHATWG same identity vs SCP-like rewritten to ssh:// vs relative join vs GitHub host hiding path semantics)
reproducibility: source-backed PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — SourceId identity and fetch URL are different objects after the conversion; leftover ssh:// changes home-relative vs absolute path
ecosystem: cargo / git submodule
mechanism_family: scp-to-ssh-rewrite, leftover-fetch-url, gitremote-whatwg-only

Packet is the failing world only. Do not assume a root cause.
