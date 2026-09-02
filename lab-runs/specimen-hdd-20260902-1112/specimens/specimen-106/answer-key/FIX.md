KNOWN FIX (sealed): pdm-project/pdm PR 2874 merge 931de2106b37e8dc55efb84de6bf7a704ad28842.

failing_ref is merge parent cc17967ace76ff2fdf455106a6eb26da50685260.

format_lockfile rewrote FileRequirement.url only when path was already absolute. extras_require mutated the shared install_requires list.

PR repair: relative_to only when path.is_absolute(); always relative_path_to_url on success; extras copy install_requires[:].

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
