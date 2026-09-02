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
