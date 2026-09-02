# Reduced excerpt of Cache::load on failing_ref
# src/cargo/util/rustc.rs

#[derive(Serialize, Deserialize, Debug, Default)]
struct CacheData {
    rustc_fingerprint: u64,
    outputs: HashMap<u64, Output>,
    successes: HashMap<u64, bool>,
}

// Cache::load:
//   rustc_fingerprint = rustc_fingerprint(wrapper, workspace_wrapper, rustc, rustup_rustc, gctx)
//   read cache_location as CacheData
//   if data.rustc_fingerprint == rustc_fingerprint {
//       debug!("reusing existing rustc info cache");
//       dirty = false;
//       data
//   } else {
//       debug!("different compiler, creating new rustc info cache");
//       empty  // CacheData { rustc_fingerprint, outputs: {}, successes: {} }
//   }

// Rustc::new then:
//   cmd = rustc (wrapped) -vV
//   verbose_version = cache.cached_output(&cmd, 0)?.0
