repository: swc-project/swc
issue: https://github.com/swc-project/swc/pull/12166
pr: https://github.com/swc-project/swc/pull/12166
failing_ref (parent of squash): c5235516340959f703c02d91a79ba40df897eb9c
fixed_ref (cache key is configured envs map, sorted): c0b6f12fe4c3b1d0235a64496560941751e21bd8
merged_at: 2026-09-01T05:52:37Z
pr_author: davidmurdoch
merged_by: kdy1
changed_files: crates/swc/src/config/mod.rs, crates/swc/tests/simple.rs, .changeset/fix-optimizer-env-cache-key.md
pr_title: fix(swc): key optimizer env cache by configured values
scout_note: not 082/090/156. leftover optimizer envs after second compile because key was vars. unique vs 001-166.
