# TASK

Salt `salt.crypt.get_rsa_key(path, passphrase)` can keep the identity of a **previous RSA private key** after the file on disk was rotated and the loaded key should have been different. The memoize cache is keyed on `(path, passphrase)` only. On-disk mtime is not part of that key. A rewritten `minion.pem` in the same process still returns the leftover previous key object until the process restarts.

On failing_ref `6e83268b7001de0b4847f8623791b9363a83d103`:

```
@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    """
    Read a private key off the disk. we memoize the constructed private key
    based on the input args.
    """
    return PrivateKey.from_file(path, passphrase).key
```

`salt.utils.decorators.memoize` is a plain str-keyed dict. Path and passphrase are not the file identity. `_auth_singleton_key` still threads `str(os.path.getmtime(keypath))` for a *different* cache and does not compensate.

Public report (saltstack/salt#69941). Write PEM; `get_rsa_key`; rewrite PEM and bump mtime; second `get_rsa_key` returns leftover previous public bytes. 3006.x two-layer helper memoized `(path, mtime, passphrase)` and evicted.

In-tree after the repair (not on failing_ref): `_get_key_with_evict(path, timestamp, passphrase)` is the memoized function; `get_rsa_key` supplies `str(os.path.getmtime(path))`.

Case A — second call, same file, same mtime:
  cache identity is current
  not leftover-after-rotation

Case B — file rewritten, leftover memoize hit:
  leftover: previous RSA private-key object / previous public bytes
  mtime omitted from memoize key
  same process

Case C — new process / memoize cache empty:
  fresh key identity
  not leftover previous key

Case D — memoize key includes mtime (post-repair shape, not on failing_ref):
  new key material after rotation
  not leftover previous key

The developer wants to know which identity case B actually used for the private key after the file change: leftover previous-memoize object (mtime omitted), current on-disk key, or omitted (no cache).
