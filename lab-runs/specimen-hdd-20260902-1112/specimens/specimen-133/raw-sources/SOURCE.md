repository: stylelint/stylelint
issue: https://github.com/stylelint/stylelint/issues/2908
pr: https://github.com/stylelint/stylelint/pull/6356
failing_ref (parent of squash on main): 3df16ba23b1cdb7b3257fa4b4979b8d0b3ffbb66
fixed_ref (Fix cache refresh when config is changed): 5be33b779b93761d86cb871dfd70f34686b5f6c5
merged_at: 2022-09-27T17:37:48Z
pr_author: kimulaco
merged_by: jeddy3
changed_files: lib/standalone.js, lib/utils/FileCache.js, lib/lintSource.js, lib/createStylelint.js, lib/__tests__/standalone-cache.test.js
pr_title: Fix cache refresh when config is changed
scout_note: not 132 eslint plugin-meta toJSON. not 114 ruff nested pyproject. Distinct leftover: standalone hashed empty CLI config so leftover .stylelintcache after cosmiconfig file change is treated as current. job-0569 unique vs 001-132.
