ACCEPT_R1

contrastiveness: high (defined current vs leftover Qundef after helper fail vs never-registered missing vs remove-after-fail)
reproducibility: source-backed issue+PR + pinned parent; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — leftover same-name helper vs moved definition JOIN of Qundef const_entry, $LOADED_FEATURES, autoload retry; two greps cannot replace
ecosystem: ruby / autoload
mechanism_family: leftover-same-name-helper, leftover-autoload-after-fail, qundef-const-entry

Packet is the failing world only. Do not assume a root cause.
