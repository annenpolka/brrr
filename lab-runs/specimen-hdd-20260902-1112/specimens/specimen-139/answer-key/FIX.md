KNOWN FIX (sealed): psf/black PR 5152 squash d246367ab471cd56298407858661d475c33b3e36.

failing_ref is parent c77093e228ff21a93638b42356aa0a4d2713aa17.

find_project_root @lru_cache keyed (srcs, stdin_filename) and resolved Path.cwd() inside the cached function when srcs was empty, so leftover project-root pyproject after a CWD change stayed current.

PR repair: resolve CWD and absolute srcs before the cache key; cache only fully-resolved paths.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
