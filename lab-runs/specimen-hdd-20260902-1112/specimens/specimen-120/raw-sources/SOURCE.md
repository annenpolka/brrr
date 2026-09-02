repository: prefix-dev/pixi
issue: https://github.com/prefix-dev/pixi/issues/3758
pr: https://github.com/prefix-dev/pixi/pull/3782
failing_ref (squash parent): 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
fixed_ref (squash merge): 804d2360157ca9c3d9197a4519ea803d28220e59
merged_at: 2025-05-20T07:56:04Z
pr_author: nichmor
merged_by: ruben-arts
changed_files: crates/pixi_manifest/src/task.rs, crates/pixi_manifest/src/toml/task.rs, src/cli/run.rs, src/task/executable_task.rs, src/task/task_hash.rs, tests/integration_python/test_run_cli.py
pr_title: fix: take into account tasks arguments when caching
scout_note: not specimen-115 go-task leftover wildcard checksum omitting MATCH. Distinct leftover: pixi task cache filename keyed by run-environment+task-name, omitting rendered args.
