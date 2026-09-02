ACCEPT_R1

contrastiveness: high (first compile last-write matches file vs leftover extra Analysis after gz switch vs delete+restore discoveredMainClasses fail vs cleanFull)
reproducibility: source-backed issue+PR + pinned merge parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — last-write Analysis identity and analysis-file identity (size+mtime) are different objects; leftover extra Analysis blocked discoveredMainClasses
ecosystem: sbt / zinc
mechanism_family: leftover-extra-analysis, last-write-cache, omitted-file-identity

Packet is the failing world only. Do not assume a root cause.
