CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public ansible-collections/community.general#9710 (closed 2025-02-17). PR 9760 squash `d696bb7b8992bfc6535c5e51dd37a00b9b4e22df` (parent `94e1511005e621f56002f3b057d03b46f7639fb3`). Local ansible/proxmox was not performed on this lab host.

Issue body: proxmox inventory cache enabled; create LXC; `meta: refresh_inventory` updates in-memory inventory; cache file under `.cache` does not change; second play fails `hostvars['debian-t']` undefined until cache deleted.

On failing_ref, `_get_json` keys cache by inventory file path. Refresh sets `cache=False` so `use_cache` is false and the plugin refetches, but there is no separate persist path. Nested assignment into an existing cache dict leaves the previous jsonfile.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible-core#73699 leftover inventory vs `--flush-cache` (core manager, not proxmox file-keyed jsonfile).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 94e1511005e621f56002f3b057d03b46f7639fb3
# plugins/inventory/proxmox.py parse / _get_json / get_cache_key(path)

# public shape:
# leftover inventory cache file after meta:refresh_inventory
# cache keyed by inventory yaml path; new LXC omitted on second run
# until cache dir deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.

ansible-collections/community.general
  plugins/inventory/proxmox.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  community.general.proxmox cache: true
  leftover inventory jsonfile after new LXC + refresh_inventory

Case A (second load, Proxmox unchanged):
  current cache identity
  not leftover-after-world-change

Case B (new LXC, leftover cache file):
  leftover: previous proxmox inventory JSON
  cache keyed by inventory file path
  new hostname omitted on second run

Case C (cache off / cache dir deleted):
  fresh inventory identity
  not leftover previous hosts

Case D (refresh writes _cache[key] = results):
  new host present on second run
  not leftover previous inventory

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  ansible-core leftover inventory vs --flush-cache (#73699)

### proxmox_cache_failing.py

# Reduced excerpt of proxmox inventory cache on failing_ref
# plugins/inventory/proxmox.py
# 94e1511005e621f56002f3b057d03b46f7639fb3
# cache_key is inventory file path. Nested write into existing dict.
# refresh (cache=False) refetches in memory; leftover jsonfile stays.

self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')

def _get_json(self, url, ignore_errors=None):
    if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
        if self.cache_key not in self._cache:
            self._cache[self.cache_key] = {'url': ''}
        data = []
        # ... HTTP GET into data ...
        self._cache[self.cache_key][url] = data
    return make_unsafe(self._cache[self.cache_key][url])

self._populate()

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
