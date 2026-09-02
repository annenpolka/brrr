# OBSERVED

Owned fixture files/cache_lock.py. Derived from specimen-006 (CI cache retaining superseded fingerprints across lockfile updates) by changing one axis: leftover *workspace member artifacts* vs a *lockfile-only* change against the same source tree.

## Captured host execution (stdlib, no third-party packages)
```
first BUILT key 673767793f4a artifact built-with:serde = "1.0.0"
after_lock_bump FRESH key 673767793f4a artifact built-with:serde = "1.0.0"
same_key True
lock_changed True
lock_old serde = "1.0.0"
lock_new serde = "1.0.219"
```
