ACCEPT_R1

contrastiveness: high (unchanged header vs leftover BMI after rewrite vs rebuild vs ASTReader content validation)
reproducibility: source-backed PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — BMI path/mtime and header bytes are different identities; leftover module stayed current
ecosystem: clangd / C++20 modules
mechanism_family: leftover-module-bmi, omitted-ast-input-content-validation, header-rewrite-reuse

Packet is the failing world only. Do not assume a root cause.
