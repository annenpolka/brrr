ACCEPT_R1

contrastiveness: high (unique gitconfig vs shared git.store; CI expected private.com vs got github.com)
reproducibility: source-backed PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — parallel workers leaked credentials through a leftover shared path after a sibling file was already uniquified
ecosystem: ruby
mechanism_family: race-test, shared-temp-path, parallel-ci

Packet is the failing world only. Do not assume a root cause.
