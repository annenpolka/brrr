ACCEPT_R1

contrastiveness: high (chart default `data: {}` drops user `baz: ~` from `.Values.data`; chart default `data: ~` keeps `baz:<nil>`; v4 vs v3 quote of the same files)
reproducibility: source-backed issue/PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — same user null is omitted or present-nil depending on whether the chart default was an empty map or YAML null
ecosystem: helm / go templates
mechanism_family: empty-map-default, user-null-omitted, coalesce-nil-identity

Packet is the failing world only. Do not assume a root cause.
