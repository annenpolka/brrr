KNOWN FIX (sealed): oven-sh/bun PR 36304 squash 079d1d345fd1e9fc54b4e0bd36a0ce57fdcf0a48.

failing_ref is squash first parent b4ee407a256ac2e4f4f3a5419387b43815cf6be7.

Repair excludes catalog-tagged deps from value-rewrite in edit_update_no_args and named bun update. New catalog walkers edit root catalog/catalogs (top-level or workspaces.*) around install. Identity is (catalog name, dependency name). bun add still replaces catalog: on purpose. Follow-up #36379 re-resolves catalog: from the workspace root without --latest.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
