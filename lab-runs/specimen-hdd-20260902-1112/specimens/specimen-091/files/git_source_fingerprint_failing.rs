// Reduced excerpt of GitSource::fingerprint on failing_ref
// src/cargo/sources/git/source.rs
// Identity for rebuild detection is the locked git oid, not a checkout PathBuf.

    fn fingerprint(&self, _pkg: &Package) -> CargoResult<String> {
        match &*self.locked_rev.borrow() {
            Revision::Locked(oid) => Ok(oid.to_string()),
            _ => unreachable!("locked_rev must be resolved when computing fingerprint"),
        }
    }
