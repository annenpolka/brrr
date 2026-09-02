# Reduced excerpt of Tree hoist on failing_ref
# src/install/lockfile/Tree.rs
# When an optional-peer slot is still invalid, hoist looks for a sibling
# already in the tree rather than skipping the edge.

                if pkg_id == invalid_package_id {
                    if dependency.behavior.is_optional_peer() {
                        break 'hoisted Tree::hoist_dependency::<true, METHOD>(
                            next_id,
                            hoist_root_id,
                            pkg_id,
                            dep_id,
                            builder,
                        )?;
                    }

                    // skip unresolvable dependencies
                    continue 'dep;
                }

            if package_id == invalid_package_id {
                debug_assert!(dependency.behavior.is_optional_peer());
                debug_assert!(res_id != invalid_package_id);
                // resolve optional peer to builder.resolutions[dep_id]
                return Ok(HoistDependencyResult::Resolve(res_id));
            }
