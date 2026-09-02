# OBSERVED

Public dprint/dprint#1135 (closed 2026-05-31). PR 1138 squash `0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f` (parent `6fc0a066370e2c3a2a1030c56fbc229918a45cef`). Local dprint was not performed on this lab host.

Issue body: exec plugin `cacheKeyFiles` is hashed into plugin Configuration.cache_key but the host incremental hash uses the raw dprint.jsonc plugin map, so leftover cache after rustfmt.toml change is reused.

On failing_ref, `incremental_hash` hashes `format_config.plugin` only. `serialized_resolved_config` is **not** on the failing revision. It is added by PR 1138.

Not this packet: specimen-132 eslint leftover plugin name@version omitted from toJSON. specimen-133 stylelint leftover cache hashing empty CLI config. specimen-114 ruff leftover cache vs nested pyproject.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
