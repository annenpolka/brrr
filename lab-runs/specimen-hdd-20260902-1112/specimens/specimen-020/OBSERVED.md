# OBSERVED

Owned fixture files/patch_insert.py. Transfer of pnpm/pnpm#14343 (Rust patch applier in a Node package-manager install) into a stdlib Python applier.

Public contrast from that PR (not a local pnpm run): given `first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@` / `+inserted` must yield `first\nsecond\ninserted\nthird\n`. The affected applier yielded `first\ninserted\nsecond\nthird\n` and still reported a successful install, including `--frozen-lockfile`.

## Captured host execution (stdlib, no third-party packages)
```
orig 'first\nsecond\nthird\n'
hunk @@ -2,0 +3 @@ +inserted
result 'first\ninserted\nsecond\nthird\n'
apply_exit 0
frozen_lockfile_install success
```
