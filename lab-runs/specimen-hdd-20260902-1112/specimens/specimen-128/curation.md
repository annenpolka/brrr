ACCEPT_R1

contrastiveness: high (unchanged workspace vs leftover mapping after add vs wipe vs missing-member invalidates)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package_config mapping identity and workspace pubspec identity are different objects; missing members omitted so leftover mapping stayed current
ecosystem: dart / pub
mechanism_family: leftover-package-config, omitted-workspace-member, lock-up-to-date-root-only

Packet is the failing world only. Do not assume a root cause.
