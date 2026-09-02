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
