# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public dprint/dprint#1135 (closed 2026-05-31). PR 1138 squash `0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f` (parent `6fc0a066370e2c3a2a1030c56fbc229918a45cef`). Local dprint was not performed on this lab host.

Issue body: exec plugin `cacheKeyFiles` is hashed into plugin Configuration.cache_key but the host incremental hash uses the raw dprint.jsonc plugin map, so leftover cache after rustfmt.toml change is reused.

On failing_ref, `incremental_hash` hashes `format_config.plugin` only. `serialized_resolved_config` is **not** on the failing revision. It is added by PR 1138.

Not this packet: specimen-132 eslint leftover plugin name@version omitted from toJSON. specimen-133 stylelint leftover cache hashing empty CLI config. specimen-114 ruff leftover cache vs nested pyproject.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6fc0a066370e2c3a2a1030c56fbc229918a45cef
# crates/dprint/src/resolution.rs PluginWithConfig::incremental_hash

# public shape:
# leftover incremental cache after rustfmt.toml listed in cacheKeyFiles changes
# resolved plugin cache_key omitted; raw dprint.jsonc map hashed
# dprint fmt does not reformat until clear-cache
```

Source-backed only. Do not execute untrusted checkouts on the host.

dprint/dprint
  crates/dprint/src/resolution.rs
  crates/dprint/src/plugins/implementations/mod.rs
  dprint.jsonc
  rustfmt.toml

RELEVANT MATERIAL

### incremental_hash_failing.rs

// Reduced excerpt of PluginWithConfig::incremental_hash on failing_ref
// crates/dprint/src/resolution.rs
// 6fc0a066370e2c3a2a1030c56fbc229918a45cef
// Raw plugin config map hashed. Resolved cache_key omitted.

  pub fn incremental_hash(&self, hasher: &mut impl Hasher) {
    hasher.write(self.info().name.as_bytes());
    hasher.write(self.info().version.as_bytes());
    let sorted_config = self.format_config.plugin.iter().collect::<BTreeMap<_, _>>();
    for (key, value) in sorted_config {
      hasher.write(key.as_bytes());
      value.hash(hasher);
    }
    // no hasher.write(serialized_resolved_config.as_bytes())
    if let Some(associations) = &self.associations {
      for association in associations {
        hasher.write(association.as_bytes());
      }
    }
    self.format_config.global.hash(hasher);
  }

### leftover_identity_split.txt

Registry / fixture:
  dprint.jsonc exec cacheKeyFiles: [./rustfmt.toml]
  leftover incremental cache after rustfmt.toml change

Case A (second dprint fmt, same rustfmt.toml):
  current cache identity
  not leftover-after-cacheKeyFiles-change

Case B (rustfmt.toml flipped, leftover cache):
  leftover: previous formatter output
  resolved plugin cache_key omitted (raw dprint.jsonc map only)
  files not reformatted

Case C (dprint clear-cache):
  fresh cache identity
  not leftover previous config

Case D (resolved config in incremental hash):
  cache miss after cacheKeyFiles change
  not leftover previous output

Not this packet:
  eslint leftover plugin name@version omitted from toJSON (specimen-132)
  stylelint leftover cache hashing empty CLI config (specimen-133)
  ruff leftover cache vs nested pyproject (specimen-114)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
