# OBSERVED

Public systemd/systemd#43355 (merged 2026-08-13). Squash `f4284e9cebac67ad7af3bc27b736cf1107b88127` (parent `cad2c455ec1acff29a81421c58adbe0ffc191f65`). Follow-up for `cf7d80a5fe549d4db11800015e02220dccec3096` (SYSTEMD_UNIT_PATH colon-separated prepend/append). Local systemd was not performed on this lab host.

PR title: path-lookup: reject empty env path components. Only trailing empty components have special meaning: they request appending the built-in defaults. Share validation between path lookup and systemd-analyze verify.

On failing_ref, `get_paths_from_environ` documents the FIXME and still splits empty components. Unset vs empty `""` vs `:` vs `::` are different getenv identities; empty components become leftover cwd.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty-override. compose leftover listed-without-equals vs image ENV (packed this tick as leftover empty-vs-unset environment, not PATH cwd).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
