KNOWN FIX (sealed): jdx/mise PR 10114 merge f38bab024878162972660d16935ac5cc8340a582.

failing_ref is squash parent 2386ef0c17e5cd5972a7d2ea2cfdf7f613e1cd4c.

Upgrade cleanup called get_versions_needed_by_tracked_configs(config, false, false), so sibling lock pins were omitted from the keep-set.

PR repair: get_versions_needed_by_tracked_configs_excluding_locks with use_locked_version=true except upgraded_config_paths. e2e sibling foo/bar dummy locks.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
