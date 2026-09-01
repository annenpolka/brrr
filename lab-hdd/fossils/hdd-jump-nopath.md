# Fossil: hdd-jump-nopath

- At: 2026-09-02 02:16:35 JST
- Decision: KILL
- Classification: THIN_WRAPPER
- Core operation: set and declare values in a key-value config store and validate them
- Nearest existing operation: etcd/consul/a json config API
- Observable delta: none that preserves stated's tree-disagreement question without a private store
- Reason: the jump replaced the working-tree object with a kv service; no untested tree-native delta remains
- HDD Jump: removed stable path identity. Did not produce a competing tree-native implementation.
- Do not send back to R1 with "make this more novel".
