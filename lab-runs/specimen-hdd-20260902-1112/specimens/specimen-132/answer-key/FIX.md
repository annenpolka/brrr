KNOWN FIX (sealed): eslint/eslint PR 16992 squash 1665c029acb92bf8812267f1647ad1a7054cbcb4.

failing_ref is parent b3634f695ddab6a82c0a9b1d8695e62b60d23366.

toJSON serialized plugins as Object.keys(plugins) only, so leftover cache after plugin upgrade kept previous-plugin lint results.

PR repair: serialize plugins as namespace:getObjectId(plugin) (name@version / meta.name+meta.version).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
