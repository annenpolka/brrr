repository: saltstack/salt
issue: https://github.com/saltstack/salt/issues/69941
pr: https://github.com/saltstack/salt/pull/69943
failing_ref (parent of squash on 3008.x): 6e83268b7001de0b4847f8623791b9363a83d103
fixed_ref (restore mtime eviction helper): 6cf49f5364e5e716852a747682196646c8af1801
merged_at: 2026-08-09T05:20:15Z
pr_author: dwoz
merged_by: dwoz
changed_files: salt/crypt.py, tests/pytests/unit/crypt/test_crypt_cryptography.py, changelog/69941.fixed.md
pr_title: Restore mtime-based eviction on get_rsa_key
scout_note: not 136 pants process cache / not 139 black CWD lru. leftover RSA key after rotation because mtime omitted from memoize key. unique vs 001-145.
