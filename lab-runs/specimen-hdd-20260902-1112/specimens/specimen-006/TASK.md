# TASK

Linux CI Rust caches for a workspace grow across lockfile updates. Fallback restores keep older fingerprints for workspace members next to newly compiled artifacts. Disk usage climbs; it is unclear which cache entries are still live for the current lockfile.

The developer wants to distinguish current workspace outputs from superseded fingerprints without deleting the whole cache.
