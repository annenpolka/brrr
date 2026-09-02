ACCEPT_R1

contrastiveness: high (in-TTL fetch vs leftover previous-version checksum after TTL vs versioned key miss vs wipe fingerprints)
reproducibility: source-backed PR + pinned squash parent/commit + cherry-pick 9210; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — package identity and version identity are different objects; leftover metadata poisoned TOFU for the new version
ecosystem: swift / package-registry
mechanism_family: leftover-metadata-cache, inverted-ttl, omitted-version, tofu-fingerprint

Packet is the failing world only. Do not assume a root cause.
