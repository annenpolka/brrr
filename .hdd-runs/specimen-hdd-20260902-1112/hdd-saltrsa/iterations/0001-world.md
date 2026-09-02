# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public saltstack/salt#69941 (closed 2026-08-31). PR 69943 squash `6cf49f5364e5e716852a747682196646c8af1801` (parent `6e83268b7001de0b4847f8623791b9363a83d103`). Local salt was not performed on this lab host.

Issue body: 3008.x PKI refactor collapsed the two-layer helper into a single decorated `get_rsa_key(path, passphrase)`. Rotated key file; same process; leftover previous key until restart. Reproduction writes two PEMs with `os.utime` and asserts public bytes differ.

On failing_ref, `@memoize` keys only path+passphrase. Nested `_auth_singleton_key` still has mtime for AsyncAuth and is a different cache.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-139 black leftover project-root vs omitted CWD on lru_cache.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 6e83268b7001de0b4847f8623791b9363a83d103
# salt/crypt.py get_rsa_key / PrivateKey.from_file

# public shape:
# leftover RSA key object after on-disk rotation
# memoize key is (path, passphrase); mtime omitted
# new process yields the new key
```

Source-backed only. Do not execute untrusted checkouts on the host.

saltstack/salt
  salt/crypt.py
  salt/utils/decorators/__init__.py

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  salt.crypt.get_rsa_key process memoize
  leftover RSA key after on-disk rotation

Case A (second call, same file, same mtime):
  current cache identity
  not leftover-after-rotation

Case B (PEM rewritten, leftover memoize hit):
  leftover: previous RSA private-key object
  mtime omitted from memoize key
  same process

Case C (new process / empty memoize):
  fresh key identity
  not leftover previous key

Case D (memoize key includes mtime):
  new key after rotation
  not leftover previous key

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  black leftover project-root vs omitted CWD (specimen-139)

### rsa_key_failing.py

# Reduced excerpt of get_rsa_key memoize on failing_ref
# salt/crypt.py
# 6e83268b7001de0b4847f8623791b9363a83d103
# memoize key is (path, passphrase). mtime omitted.
# leftover previous key object after PEM rotation in-process.

@salt.utils.decorators.memoize
def get_rsa_key(path, passphrase):
    return PrivateKey.from_file(path, passphrase).key

# _auth_singleton_key still has mtime for a *different* cache
# and does not evict get_rsa_key

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
