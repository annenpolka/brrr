KNOWN FIX (sealed): dprint/dprint PR 1138 squash 0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f.

failing_ref is parent 6fc0a066370e2c3a2a1030c56fbc229918a45cef.

incremental_hash hashed the raw plugin config map and omitted the plugin's resolved Configuration.cache_key, so leftover incremental cache after a cacheKeyFiles change kept previous formatter output.

PR repair: hash serialized_resolved_config from instance.resolved_config.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
