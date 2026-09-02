# OBSERVED

Source: test `python_find_cached_launcher_override` at
`c5d8a25374a5b3c98178ebcb440c8c25f65b803e`, plus issue 21062. Local
execution was not performed.

Harness snapshot (failing revision):

```
# with PYTHONEXECUTABLE=<.venv>/bin/python3
uv python find <other>/bin/python3
----- stdout -----
[VENV]/bin/python3

# PYTHONEXECUTABLE removed
uv python find <other>/bin/python3
----- stdout -----
[VENV]/bin/python3
```

The second command's comment in the test says it should return `other`,
not the cached `.venv`. The recorded stdout is still `[VENV]/bin/python3`.

Issue 21062 (related field report): `uv run --project slack-watcher
<console-script>` executed a binary under a *deleted* worktree path
`A/slack-watcher/.venv/bin/...` while the live project was at `B`.
`uv run --no-cache` was correct. Deleting only
`~/.cache/uv/interpreter-v4` also corrected subsequent runs. Decoding
`.msgpack` entries showed `sys_prefix` / `sys_executable` pointing at
the deleted worktree `A`.
