KNOWN FIX (sealed): saltstack/salt PR 69943 squash 6cf49f5364e5e716852a747682196646c8af1801.

failing_ref is parent 6e83268b7001de0b4847f8623791b9363a83d103.

get_rsa_key was @memoize on (path, passphrase) only. Rotated PEM kept leftover previous key object in-process. mtime was not part of the memoize identity.

PR repair: restore _get_key_with_evict(path, timestamp, passphrase) as the memoized helper; get_rsa_key passes str(os.path.getmtime(path)).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
