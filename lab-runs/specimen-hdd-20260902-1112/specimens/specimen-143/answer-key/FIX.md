KNOWN FIX (sealed): ansible-collections/community.general PR 9760 squash d696bb7b8992bfc6535c5e51dd37a00b9b4e22df.

failing_ref is parent 94e1511005e621f56002f3b057d03b46f7639fb3.

Proxmox inventory cache was keyed by inventory file path and had only a use_cache knob. meta:refresh_inventory refetched in memory but leftover previous jsonfile stayed current for the next run.

PR repair: update_cache when cache=False but plugin cache enabled; assign self._cache[self.cache_key] = self._results in one go.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
