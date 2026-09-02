# Reduced excerpt of Package::clone on failing_ref
# src/install/lockfile/Package.rs
# Lockfile::clean_with_logger rebuilds packages by cloning from the root.
# resolutions[i] is the resolved package ID for dependencies[i].

        let resolutions: &mut [PackageID] =
            &mut new.buffers.resolutions[prev_len as usize..end as usize];
        debug_assert_eq!(old_resolutions.len(), resolutions.len());
        for (i, (old_resolution, resolution)) in old_resolutions
            .iter()
            .zip(resolutions.iter_mut())
            .enumerate()
        {
            if *old_resolution >= max_package_id {
                *resolution = invalid_package_id;
                continue;
            }

            let mapped = package_id_mapping[*old_resolution as usize];
            if mapped < max_package_id {
                *resolution = mapped;
            } else {
                cloner.clone_queue.push(PendingResolution {
                    old_resolution: *old_resolution,
                    resolve_id: new_package.resolutions.off
                        + PackageID::try_from(i).expect("int cast"),
                });
            }
        }
