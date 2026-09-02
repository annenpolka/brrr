# OBSERVED

Public biomejs/biome#11409 (merged 2026-08-19). Squash `405dedb0ff65dd29927faf587f6542e3c29db248` (parent `7dbf9d84125b51c4177a899f8638d54b01cd065c`). Local biome was not performed on this lab host.

PR title: fix(core): files eviction and project. Closing a file would not evict the parsed-source map from the database. Changeset: LSP memory leak over long editor sessions.

On failing_ref, `close_file` removes `documents` and `node_cache` only. Parsed-source map stays. Project close unloads documents under the root but omitted descendant files-map eviction.

Not this packet: specimen-157 jest haste mock-name delete. specimen-159 gleam leftover cache files after move+restore.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
