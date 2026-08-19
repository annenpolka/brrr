# moor

Bind a log instance to a current locator **and** a source hole in one pass.

A CI or compiler line is not a path and is not a string. It is an *instance*: interpolated values plugged into a format template, observed at a `file:line` that may already be stale. `slip` relocates addresses. `unfmt` / `sluice` invert strings against templates. **moor** is the joint verb: re-berth the instance against two snapshots so the locator and the hole assignment corroborate.

## Install / run

```bash
chmod +x ./moor
./moor --help
./demo.sh
```

Single Python 3 file. `git` is optional when both `--from-dir` and `--to-dir` are set.

```
moor --from <ref> [--to <ref>] < yesterday.ci.log
moor --from-dir old/ --to-dir new/ --porcelain 'src/auth.py:5: user 42 not found'
```

Exit 0 on success. `--strict` exits 1 if a record is a miss or an unresolved locator. Confirmed deletions are answers.

## Examples

Rewrite a mixed rustc / panic / traceback log. Stale `file:line` moves; filled-in messages unpack:

```bash
cat ci.log | ./moor --repo ~/src/kizu --from b4e6a5d --to HEAD
#   --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5  ⟦… no method named {}  0=seen_hunk_fingerprint⟧
# thread 'git::diff' panicked at src/git/diff.rs:34:28:
# git diff single file failed: fatal: not a git repository …  ⟦… git diff single file failed: {}  0=fatal: …⟧
```

Ask one line what it is. The test suite's exact literal `user 42 not found` is a better raw inverse-printf match; the stale locator pulls the bind onto the production template after the file split:

```bash
./moor --repo . --from v1 --to HEAD --porcelain \
  'src/auth.py:5: user 42 not found'
# bound  src/auth.py:5  src/users/lookup.py:5  user {uid} not found  uid=42
```

Two directories, no git:

```bash
./moor --from-dir old-tree --to-dir new-tree \
  --porcelain 'src/old.py:2: open /tmp/x: permission denied'
# bound  src/old.py:2  pkg/new.py:2  open {path}: {err}  path=/tmp/x err=permission denied
```

`--records auto` (default) groups a rustc `error` + `-->` pair, a `panicked at path:line:` + next line, and a Python traceback + exception, so the message and the locator score as one instance. `--records line` is the old one-line filter. `--json` / `--porcelain` emit bindings instead of a rewritten stream.
