# OBSERVED

Source: https://github.com/astral-sh/uv/issues/19705 at uv 0.11.16, and
`crates/uv-cache-info/src/git_info.rs` at
`6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf`. Local execution was not
performed.

After `uv sync` in a linked worktree vs a regular clone of the same
commit (timestamps elided):

```jsonc
// linked worktree
{"commit": null, "tags": {"v0.1.0": "c3aff651..."}, "env": {}, "directories": {}}

// regular clone
{"commit": "c3aff651...", "tags": {}, "env": {}, "directories": {}}
```

In the worktree, later `git commit` then `uv sync` keeps the hatch-vcs
version unchanged. In the regular clone, the same sequence rebuilds.

Secondary observation from the same report: after `git pack-refs --all`
in the regular clone, a re-sync records `"commit": null` there too.
Tags in the clone were empty even though `v0.1.0` existed (packed).

Loose-ref layout that *does* invalidate in `invalidate_path_on_commit`
(regular `.git` directory, not a worktree file):

```
.git/HEAD                    -> "ref: refs/heads/main"
.git/refs/heads/main         -> 40-hex commit
```

Changing that loose ref file caused `uv pip install -r requirements.txt`
to re-prepare the editable path dependency.
