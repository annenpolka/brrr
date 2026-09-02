ACCEPT_R1

contrastiveness: high (first install writes abandoned vs leftover same-version omit vs wipe+reinstall vs real version bump)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — lock abandoned identity and installed.json abandoned identity are different objects; leftover installed identity hid audit
ecosystem: php / composer installer
mechanism_family: leftover-installed-json, omitted-abandoned-state, same-version-skip

Packet is the failing world only. Do not assume a root cause.
