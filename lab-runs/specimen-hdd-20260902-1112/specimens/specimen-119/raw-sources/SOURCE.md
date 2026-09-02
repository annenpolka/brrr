repository: prefix-dev/pixi
issue: https://github.com/prefix-dev/pixi/issues/3758
pr: https://github.com/prefix-dev/pixi/pull/3782
failing_ref (squash-merge first parent): 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
fixed_ref (squash merge commit): 804d2360157ca9c3d9197a4519ea803d28220e59
pr_head: e980778e0b2993b3d12de4736a2b8b3992086829
merged_at: 2025-05-20
merged_by: ruben-arts
pr_author: nichmor
changed_files: src/task/executable_task.rs, src/task/task_hash.rs, src/cli/run.rs, tests/integration_python/test_run_cli.py, crates/pixi_manifest/src/task.rs
pr_title: fix: take into account tasks arguments when caching
scout_note: not specimen-115 (go-task leftover wildcard checksum omitting MATCH, go-task/task#1795 / PR 1808). not 076/088/104 gradle. leftover here is cache *filename* identity omitting rendered task args, while computation_hash inside the file already includes input/output file hashes.
