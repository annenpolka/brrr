ACCEPT_R1

contrastiveness: high (success apply keeps identity vs destroy-error omits vs mark-only omits vs error-null DeepCopy keeps)
reproducibility: source-backed PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — value identity and resource identity are different objects; leftover omitted identity after apply while value remains
ecosystem: terraform / go
mechanism_family: leftover-identity-omitted, apply-drops-identity, mark-only-update

Packet is the failing world only. Do not assume a root cause.
