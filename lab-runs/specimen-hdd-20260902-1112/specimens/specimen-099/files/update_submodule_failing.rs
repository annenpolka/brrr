// Reduced excerpt of GitCheckout::update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// e91b2baa632c0c7e84216c91ecfe107c37d887c1
// Nested submodule is fetch+reset into the checkout. No GitDatabase / git/db ident.

            let reference = GitReference::Rev(head.to_string());
            gctx.shell()
                .status("Updating", format!("git submodule `{child_remote_url}`"))?;
            fetch(
                &mut repo,
                &child_remote_url,
                &reference,
                gctx,
                RemoteKind::GitDependency,
            )?;
            let obj = repo.find_object(head, None)?;
            reset(&repo, &obj, gctx)?;
            update_submodules(&repo, gctx, &child_remote_url)
