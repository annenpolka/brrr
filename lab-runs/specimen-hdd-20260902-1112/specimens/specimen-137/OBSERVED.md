# OBSERVED

Public python/mypy#16652 (closed 2025-09-06). PR 19801 merge `309b01e287e3afabeb888572455f9bf55d86acad` (parent `8f2371a565eb9c29f03922b26da8eab054fbbcf8`). Local mypy was not performed on this lab host.

Issue body: same command different results depending on leftover cache; Super-exclude errors on a cold cache; after a successful `bug` exclude run, Super-exclude succeeds until `.mypy_cache` is deleted.

On failing_ref, OPTIONS_AFFECTING_CACHE ends at `fixed_format_cache`. `untyped_calls_exclude` is **not** in that set. It is added by PR 19801.

Not this packet: specimen-067 mypy leftover sentinels (issue 21866 / PR 21888 expandtype). specimen-075 rustc incremental. specimen-136 pants vcs_version process cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
