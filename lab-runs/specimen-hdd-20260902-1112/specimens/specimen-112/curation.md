ACCEPT_R1

contrastiveness: high (fresh install writes abandoned vs leftover omitted abandoned vs wipe+install vs version-bump reinstall)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — lock abandoned identity and installed.json abandoned identity are different objects; same-version leftover blocked audit
ecosystem: php / composer
mechanism_family: leftover-installed-json, omitted-abandon, lock-vs-installed

Packet is the failing world only. Do not assume a root cause.
