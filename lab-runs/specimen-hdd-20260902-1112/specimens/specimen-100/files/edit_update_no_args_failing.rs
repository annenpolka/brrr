// Reduced excerpt of edit_update_no_args on failing_ref
// src/install/PackageManager/PackageJSONEditor.rs
// b4ee407a256ac2e4f4f3a5419387b43815cf6be7
// Walks four dependency groups of the current package.json only.
// Tag::Catalog is admitted. Root catalog objects are not a group.

                        let mut tag = dependency::Tag::infer(version_literal);

                        // only updating dependencies with npm versions, dist-tags if `--latest`, and catalog versions.
                        if tag != dependency::Tag::Npm
                            && (tag != dependency::Tag::DistTag
                                || !manager.options.do_.contains(Do::UPDATE_TO_LATEST))
                            && tag != dependency::Tag::Catalog
                        {
                            continue;
                        }

                        let entry = manager.updating_packages.get_or_put(key_str)?;

                        if manager.options.do_.contains(Do::UPDATE_TO_LATEST) {
                            dep.value = Some(Expr::allocate(
                                arena,
                                E::EString::init(b"latest"),
                                bun_ast::Loc::EMPTY,
                            ));
                        }
