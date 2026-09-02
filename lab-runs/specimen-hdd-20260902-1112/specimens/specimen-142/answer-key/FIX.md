KNOWN FIX (sealed): ansible/ansible PR 77083 merge 94b73d66d53ca0df9911d1dd412bc1d3c9181b1b.

failing_ref is parent c9db73f04e7a5fae7bbbdff8efbd585d15971d31.

InventoryManager always parse_sources(cache=True) and _flush_cache only cleared facts, so leftover inventory cache after --flush-cache stayed current.

PR repair: InventoryManager(..., cache=(not options.get('flush_cache'))).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
