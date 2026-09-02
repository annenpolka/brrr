repository: psf/black
issue: null
pr: https://github.com/psf/black/pull/5152
failing_ref (parent of squash on main): c77093e228ff21a93638b42356aa0a4d2713aa17
fixed_ref (resolve CWD before lru_cache key): d246367ab471cd56298407858661d475c33b3e36
merged_at: 2026-06-01T16:34:38Z
pr_author: anisia19
merged_by: cobaltt7
changed_files: src/black/files.py, CHANGES.md
pr_title: fix: resolve CWD before lru_cache key in find_project_root
scout_note: not 114 ruff nested pyproject. Distinct leftover: lru_cache key omits resolved CWD so leftover project-root pyproject after CWD change is treated as current.
