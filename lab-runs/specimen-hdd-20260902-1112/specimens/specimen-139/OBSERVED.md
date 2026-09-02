# OBSERVED

Public psf/black PR 5152 squash `d246367ab471cd56298407858661d475c33b3e36` (parent `c77093e228ff21a93638b42356aa0a4d2713aa17`). Local black was not performed on this lab host.

PR body: when `srcs` is empty (`black --code`), `find_project_root` fell back to `os.getcwd()` inside `@lru_cache`. Cache key is only `(srcs, stdin_filename)`. Two calls from different directories with `srcs=()` share the leftover entry.

On failing_ref, `@lru_cache` sits on `find_project_root`. Resolved CWD is **not** part of the key. `_find_project_root_cached` is added by PR 5152.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-132 eslint leftover plugin name@version omitted from toJSON.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
