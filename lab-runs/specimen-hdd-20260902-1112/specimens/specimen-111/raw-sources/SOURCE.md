repository: microsoft/TypeScript
issue: https://github.com/microsoft/TypeScript/issues/49527
pr: https://github.com/microsoft/TypeScript/pull/49543
failing_ref (squash parent): 8ed846c73b5033087eee119ae00511e019f91729
fixed_ref (squash merge): df2192697670d2bf8840c1e4fcd51cbf8a13cee9
merged_at: 2022-06-27T22:02:11Z
pr_author: sheetalkamat
merged_by: sheetalkamat
changed_files: src/compiler/builder.ts, src/compiler/builderState.ts, plus incremental baselines
pr_title: To handle d.ts emit errors that could affect other files, in incremental mode use d.ts emit text + diagnostics as signature of the file
scout_note: not specimen-067/075. Distinct leftover: .tsbuildinfo file signature is d.ts text hash; leftover omits d.ts diagnostic identity so importer stale error remains. job-0460.
