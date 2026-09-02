KNOWN FIX (sealed): python/mypy PR 19801 merge 309b01e287e3afabeb888572455f9bf55d86acad.

failing_ref is parent 8f2371a565eb9c29f03922b26da8eab054fbbcf8.

OPTIONS_AFFECTING_CACHE omitted untyped_calls_exclude, so leftover .mypy_cache after --untyped-calls-exclude change kept previous success/error identity.

PR repair: add "untyped_calls_exclude" to OPTIONS_AFFECTING_CACHE.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
