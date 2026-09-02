// Reduced excerpt of update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// Converted child_remote_url is parsed as Url and becomes GitSource/GitRemote.

            let child_remote_url = absolute_submodule_url(parent_remote_url, child_url_str)?;
            let reference = GitReference::Rev(head.to_string());

            let source_id = SourceId::for_git(&child_remote_url.into_url()?, reference)?
                .with_git_precise(Some(head.to_string()));

            let mut source = GitSource::new(source_id, gctx)?;
            let (db, actual_rev) = source.fetch_db(true).with_context(|| {
                let name = child.name().unwrap_or("");
                format!("failed to fetch submodule `{name}` from {child_remote_url}",)
            })?;
