repository: eslint/eslint
issue: https://github.com/eslint/eslint/issues/16284
pr: https://github.com/eslint/eslint/pull/16992
failing_ref (parent of squash on main): b3634f695ddab6a82c0a9b1d8695e62b60d23366
fixed_ref (Use plugin metadata for flat config serialization): 1665c029acb92bf8812267f1647ad1a7054cbcb4
merged_at: 2023-03-23T19:47:52Z
pr_author: nzakas
merged_by: mdjermanovic
changed_files: lib/config/flat-config-array.js, tests/lib/config/flat-config-array.js, docs/src/extend/plugins.md
pr_title: feat: Use plugin metadata for flat config serialization
scout_note: not 114 ruff nested pyproject. not 107 pytest cache-dir files. Distinct leftover: serialized flat config omits plugin name@version so leftover cache after plugin upgrade is treated as current. job-0555 was other-worker SKIP; this pair is leftover plugin-meta vs cache identity.
