# OBSERVED

Public saltstack/salt#69941 (closed 2026-08-31). PR 69943 squash `6cf49f5364e5e716852a747682196646c8af1801` (parent `6e83268b7001de0b4847f8623791b9363a83d103`). Local salt was not performed on this lab host.

Issue body: 3008.x PKI refactor collapsed the two-layer helper into a single decorated `get_rsa_key(path, passphrase)`. Rotated key file; same process; leftover previous key until restart. Reproduction writes two PEMs with `os.utime` and asserts public bytes differ.

On failing_ref, `@memoize` keys only path+passphrase. Nested `_auth_singleton_key` still has mtime for AsyncAuth and is a different cache.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-139 black leftover project-root vs omitted CWD on lru_cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
