ACCEPT_R1

contrastiveness: high (IdentityJSON present + schema.Identity nil vs IdentityJSON present + identity schema with id; Encode already omits IdentityJSON when Identity is nil; type-mismatch Decode error vs successful refresh identity)
reproducibility: source-backed PR + pinned squash parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — leftover identity JSON is decoded through the current provider identity schema, which may be absent
ecosystem: terraform / go
mechanism_family: provider-schema-identity, leftover-identity-json, encode-decode-identity-guard

Packet is the failing world only. Do not assume a root cause.
