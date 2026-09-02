// Reduced excerpt of Upgrade cleanup on failing_ref
// 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c
// use_locked_version=false is applied to every tracked config.

        let versions_needed_by_tracked =
            get_versions_needed_by_tracked_configs(config, false, false).await?;

        for (o, tv) in to_remove {
            if successful_versions.iter().any(|v| v.ba() == o.tool_version.ba()) {
                let version_key = (
                    o.tool_version.ba().short.to_string(),
                    o.tool_version.tv_pathname(),
                );
                if versions_needed_by_tracked.contains(&version_key) {
                    continue;
                }
                // uninstall old version
            }
        }
