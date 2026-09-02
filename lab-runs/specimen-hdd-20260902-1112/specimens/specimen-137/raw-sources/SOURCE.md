repository: python/mypy
issue: https://github.com/python/mypy/issues/16652
pr: https://github.com/python/mypy/pull/19801
failing_ref (parent of merge on master): 8f2371a565eb9c29f03922b26da8eab054fbbcf8
fixed_ref (add untyped_calls_exclude to OPTIONS_AFFECTING_CACHE): 309b01e287e3afabeb888572455f9bf55d86acad
merged_at: 2025-09-06T00:16:36Z
pr_author: ilevkivskyi
merged_by: ilevkivskyi
changed_files: mypy/options.py, test-data/unit/check-incremental.test
pr_title: Make untyped_calls_exclude invalidate cache
scout_note: not 067 mypy sentinels. Distinct leftover: untyped_calls_exclude omitted from OPTIONS_AFFECTING_CACHE so leftover .mypy_cache after exclude change stayed current. unique vs 001-136.
