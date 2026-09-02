# OBSERVED

Public ansible/ansible#73699 (closed 2022-03-17). PR 77083 merge `94b73d66d53ca0df9911d1dd412bc1d3c9181b1b` (parent `c9db73f04e7a5fae7bbbdff8efbd585d15971d31`). Local ansible was not performed on this lab host.

Issue body: --flush-cache still passes cache=True into inventory plugins; docs say refresh should update cache. _flush_cache only clears facts.

On failing_ref, InventoryManager always parse_sources(cache=True). PR 77083 threads cache=(not flush_cache) into InventoryManager.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible#38394 leftover vars_files closed without PR.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
