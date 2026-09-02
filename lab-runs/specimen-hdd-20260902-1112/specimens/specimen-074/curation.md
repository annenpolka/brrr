ACCEPT_R1

contrastiveness: high (install exit 0 on ruby-platform nokogiri 1.18.10 vs setup miss of nokogiri-1.18.10-x86_64-linux; frozen vs unlocked lockfile contents)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — frozen install materializes a different platform identity than the locked spec, then setup looks up the locked identity
ecosystem: ruby / bundler
mechanism_family: platform-fallback-extra, frozen-lockfile-identity, ruby-variant-not-locked

Packet is the failing world only. Do not assume a root cause.
