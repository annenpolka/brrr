// Reduced excerpt of GitSource::update on failing_ref
// src/cargo/sources/git/source.rs
// 3d357a9dd6576d7108be731802282176e560d70f
// Checkout lives under $CARGO_HOME/git/checkouts/<ident>/<short-id>/.
// RecursivePathSource is constructed with that PathBuf as-is.

        let checkout_path = self
            .gctx
            .git_checkouts_path()
            .join(&self.ident)
            .join(short_id.as_str());
        let checkout_path = checkout_path.into_path_unlocked();
        db.copy_to(actual_rev, &checkout_path, self.gctx, self.quiet)?;

        let source_id = self
            .source_id
            .borrow()
            .with_git_precise(Some(actual_rev.to_string()));
        let path_source = RecursivePathSource::new(&checkout_path, source_id, self.gctx);

        self.path_source.replace(Some(path_source));
        self.short_id.replace(Some(short_id.as_str().into()));
        self.locked_rev.replace(Revision::Locked(actual_rev));
        self.path_source.borrow().as_ref().unwrap().load()?;
