# TASK

ESLint's `--cache` can keep the identity of a **previous lint result** after a plugin upgrade should have been a different cache object. Flat config serialization used as the cache identity listed plugins as namespaces only. Plugin `name@version` / `meta.name`+`meta.version` are omitted, so leftover cache after `eslint-plugin-react` 7.37.1 → 7.37.7 still hits.

On failing_ref `b3634f695ddab6a82c0a9b1d8695e62b60d23366`, `FlatConfigArray` `toJSON` does:

```
plugins: Object.keys(plugins),
```

Parser/processor objects already used `getObjectId` (name@version). Plugins did not.

Public report (eslint/eslint#16284): upgrade eslint-plugin-react; leftover cache suppresses new-rule offenses.

In-tree after the repair (not on failing_ref): serialize each plugin as `namespace:name@version` via `getObjectId`; tests convert config with plugin name/version and plugin meta into normalized JSON.

Case A — second `eslint --cache` with unchanged plugin version:
  cache identity is current
  not leftover-after-plugin-upgrade

Case B — plugin upgrade, leftover cache:
  leftover: previous plugin version's lint results
  plugin name@version omitted from serialized config identity
  new-rule offenses not reported

Case C — delete `.eslintcache` then lint:
  fresh cache identity
  not leftover previous plugin

Case D — plugin meta in serialized config (post-repair shape, not on failing_ref):
  cache miss after plugin upgrade
  not leftover previous plugin results

The developer wants to know which identity case B actually used for the ESLint cache after the plugin upgrade: leftover previous-plugin results (meta omitted), current plugin-version identity, or omitted (no cache file).
