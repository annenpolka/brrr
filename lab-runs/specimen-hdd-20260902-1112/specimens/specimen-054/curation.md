ACCEPT_R1

contrastiveness: high (numeric identity keys 119/120/211 vs named UNPACK_SEQUENCE/YIELD_VALUE/UNPACK_SEQUENCE_TWO_TUPLE on the same revision; generator uses opmap membership)
reproducibility: source-backed issue + PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — generator and generated header landed together, yet the header was not the generator's output because hand-added numeric slots collided with already-mapped opcodes
ecosystem: c / cpython
mechanism_family: generated-code-drift, stale-generated-header, regen-all

Packet is the failing world only. Do not assume a root cause.
