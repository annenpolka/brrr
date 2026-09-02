repository: aws/aws-cdk
issue: https://github.com/aws/aws-cdk/issues/21374
pr: https://github.com/aws/aws-cdk/pull/21374
failing_ref (parent of squash on main): fc8d54e866ab313b6b25b80039dff03e47d0a88c
fixed_ref (full mtime in fingerprint cache key): 65a210aaaf8f45095170bca7779fd274aab54a00
merged_at: 2022-07-29T13:33:43Z
pr_author: RomainMuller
merged_by: RomainMuller
changed_files: packages/@aws-cdk/core/lib/fs/fingerprint.ts, packages/@aws-cdk/core/test/fs/fs-fingerprint.test.ts
pr_title: fix(core): asset fingerprint cache invalidation incorrectly uses mtime
scout_note: not 139 black CWD lru / not 075 rustc fingerprint. leftover content hash after rewrite because truncated mtime was the cache identity. unique vs 001-145.
