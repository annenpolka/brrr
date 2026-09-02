ACCEPT_R1

contrastiveness: high (Windows backslash path vs git value-regex; cleanup returns success-shaped false; leftover includeIf on next run)
reproducibility: source-backed issue + PR + pinned squash parent/commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — cleanup looks like it matched an exact path, but git interpreted the path as a regex and then swallowed the error
ecosystem: typescript / actions
mechanism_family: regex-unescaped-path, git-config-unset, stale-includeif

Packet is the failing world only. Do not assume a root cause.
