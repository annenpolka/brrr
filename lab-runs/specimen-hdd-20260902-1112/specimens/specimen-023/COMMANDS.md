# COMMANDS

Not executed in this packet. Source-backed only.

Issue 19705 minimal session (macOS/Linux):

```text
git init --bare .bare -b main
git clone .bare seed
# in seed: pyproject with hatch-vcs + cache-keys git commit/tags
git add -A && git commit -m init && git tag v0.1.0
git push origin main v0.1.0
git -C .bare worktree add ../wt main
git clone .bare plain
(cd wt && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
(cd plain && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
```

Then `git commit` in `wt` and `uv sync` again; compare version / cache JSON.

Loose-ref unit test at the failing revision:

```text
cargo test -p uv --test it invalidate_path_on_commit -- --exact
```
