ACCEPT_R1

contrastiveness: high (unchanged files vs leftover dropped name after one delete vs restart crawl vs mockDuplicates survivor)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — mock name and providing file path are different identities; leftover dropped-name stayed current
ecosystem: jest / haste-map
mechanism_family: leftover-haste-mock-name, omitted-survivor-on-delete, watch-mode-name-drop

Packet is the failing world only. Do not assume a root cause.
