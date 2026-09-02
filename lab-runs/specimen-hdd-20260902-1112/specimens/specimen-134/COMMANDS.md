```
# not executed on this lab host
# failing_ref 5468dd6fb24ee98cbf6e4c05e3421e6a17e73199
# crates/core/task/src/task.rs expand_env
# crates/core/vcs/src/git.rs get_file_hashes skips is_file_ignored

# public shape:
# leftover moon task cache after .env FOO=123 -> FOO=456
# env file omitted from inputs; gitignored paths skipped from hash
# cached output reused
```

Source-backed only. Do not execute untrusted checkouts on the host.
