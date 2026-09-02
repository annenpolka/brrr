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
