repository: astral-sh/uv
issue: https://github.com/astral-sh/uv/issues/11479
pr: https://github.com/astral-sh/uv/pull/11513
failing_ref (parent of first rebased PR commit on main): 2bda549bcca67f06df602901ad9cdf30d35add00
fixed_ref (conflict-marker simplification skip): 91593d42d990397695a15750dcb8453c62a71b7d
test_commit: aaf3429e3f1ef3ba31692b50664409d1b3b6b3c1
merged_at: 2025-02-18T12:45:24Z
pr_author: BurntSushi
merged_by: BurntSushi
changed_files: crates/uv-resolver/src/graph_ops.rs, crates/uv-resolver/src/resolution/output.rs, crates/uv/tests/it/lock_conflict.rs, crates/uv/tests/it/lock.rs
pr_title: fix duplicate packages with multiple conflicting extras declared
scout_note: not extraedge/080/098 extras CLI. not specimen-006/102/106. not 123/124 earthly CACHE --id. Distinct leftover: extras conflict marker simplified to true so leftover extra-gated version is unconditional lock identity. job-0528 was coord-skipped citing uv#20078; this pair is leftover extras-marker vs lock.
