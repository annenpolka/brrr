# OBSERVED

Public ansible-collections/community.general#9710 (closed 2025-02-17). PR 9760 squash `d696bb7b8992bfc6535c5e51dd37a00b9b4e22df` (parent `94e1511005e621f56002f3b057d03b46f7639fb3`). Local ansible/proxmox was not performed on this lab host.

Issue body: proxmox inventory cache enabled; create LXC; `meta: refresh_inventory` updates in-memory inventory; cache file under `.cache` does not change; second play fails `hostvars['debian-t']` undefined until cache deleted.

On failing_ref, `_get_json` keys cache by inventory file path. Refresh sets `cache=False` so `use_cache` is false and the plugin refetches, but there is no separate persist path. Nested assignment into an existing cache dict leaves the previous jsonfile.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible-core#73699 leftover inventory vs `--flush-cache` (core manager, not proxmox file-keyed jsonfile).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
