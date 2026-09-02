# TASK

Ansible `community.general.proxmox` inventory with `cache: true` can keep the identity of a **previous inventory JSON** after the Proxmox world changed (new LXC) and `meta: refresh_inventory` should have been a different host set. The cache key is inventory **file** identity (`get_cache_key(path)`). The plugin has only `use_cache = cache and get_option('cache')`. On refresh, `cache=False` so it refetches in memory, but it does not persist a new cache file. The next playbook run hits leftover previous hosts.

On failing_ref `94e1511005e621f56002f3b057d03b46f7639fb3`:

```
self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')
# _get_json:
if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
    ...
    self._cache[self.cache_key][url] = data
return make_unsafe(self._cache[self.cache_key][url])
self._populate()
```

`get_cache_key(path)` is the inventory yaml path, not the remote host set. Nested writes into an existing `_cache[self.cache_key]` dict do not replace the cache file after refresh.

Public report (ansible-collections/community.general#9710). Create LXC; `meta: refresh_inventory`; in-memory inventory has the new host; cache file timestamp/content unchanged; second run without handler uses leftover previous inventory until the cache dir is deleted.

In-tree after the repair (not on failing_ref): `update_cache = not cache and get_option('cache')`; results collected in `_results`; `self._cache[self.cache_key] = self._results` written in one go.

Case A — second inventory load, Proxmox unchanged, cache on:
  cache identity is current
  not leftover-after-world-change

Case B — new LXC then leftover cache file (refresh did not persist):
  leftover: previous proxmox inventory JSON / missing new hostname
  cache keyed by inventory file path
  same `.cache` jsonfile

Case C — cache plugin off / cache dir deleted:
  fresh inventory identity
  not leftover previous hosts

Case D — refresh writes `_cache[cache_key] = results` (post-repair shape, not on failing_ref):
  cache miss / new host present on second run
  not leftover previous inventory

The developer wants to know which identity case B actually used for the inventory after the new LXC: leftover previous-file-keyed cache (refresh omitted persist), current Proxmox identity, or omitted (no cache).
