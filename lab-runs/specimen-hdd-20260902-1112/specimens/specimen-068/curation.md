ACCEPT_R1

contrastiveness: high (shim node loses TEST-VAR; real binary keeps it; TS CLI Unix link already preserves names)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — the bug is not “env was unset” but “the name is not a shell identifier, so the shim never forwarded it”
ecosystem: node / pnpm
mechanism_family: env-name-not-shell-identifier, shell-shim-sanitization, posix-exec

Packet is the failing world only. Do not assume a root cause.
