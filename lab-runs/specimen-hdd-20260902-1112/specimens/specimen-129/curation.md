ACCEPT_R1

contrastiveness: high (first AP compile vs leftover generated class after source delete vs wipe out/ vs plain-Java zinc mapping)
reproducibility: source-backed issue+PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — zinc source-class identity and AP-generated product identity are different objects; leftover class stayed current
ecosystem: mill / zinc / javac-apt
mechanism_family: leftover-generated-class, omitted-product-from-analysis, persistent-compile-dest

Packet is the failing world only. Do not assume a root cause.
