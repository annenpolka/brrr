ACCEPT_R1

contrastiveness: high (first set writes supporting files vs leftover exists() omit vs mkdir-then-set omit vs --cache-clear)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — directory existence and supporting-file identity are different objects; leftover dir blocked .gitignore
ecosystem: python / pytest cache
mechanism_family: leftover-cache-dir, omitted-supporting-files, exists-gate

Packet is the failing world only. Do not assume a root cause.
