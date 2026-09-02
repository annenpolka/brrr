# TASK

dprint `--incremental` can keep the identity of a **previous format cache** after a file listed in exec-plugin `cacheKeyFiles` should have been a different hash. The host `incremental_hash` hashed the raw plugin config map from `dprint.jsonc`. The plugin's resolved `Configuration.cache_key` (exec plugin folds `rustfmt.toml` contents into it) is omitted.

On failing_ref `6fc0a066370e2c3a2a1030c56fbc229918a45cef`:

```
pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
        hasher.write(key.as_bytes());
        value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config)
    self.format_config.global.hash(hasher);
}
```

Public report (dprint/dprint#1135). `cacheKeyFiles: ["./rustfmt.toml"]`; edit rustfmt.toml; leftover incremental cache; `dprint fmt` does not reformat until `dprint clear-cache`.

In-tree after the repair (not on failing_ref): `serialized_resolved_config` from `instance.resolved_config` is hashed; test `incremental_hash_includes_resolved_config`.

Case A — second `dprint fmt` with unchanged rustfmt.toml:
  cache identity is current
  not leftover-after-cacheKeyFiles-change

Case B — rustfmt.toml flipped, leftover incremental cache:
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C — `dprint clear-cache` then fmt:
  fresh cache identity
  not leftover previous config

Case D — resolved config in incremental hash (post-repair shape, not on failing_ref):
  cache miss after cacheKeyFiles change
  not leftover previous output

The developer wants to know which identity case B actually used for the incremental cache after the rustfmt.toml change: leftover previous-config results (resolved cache_key omitted), current cacheKeyFiles identity, or omitted (no cache).
