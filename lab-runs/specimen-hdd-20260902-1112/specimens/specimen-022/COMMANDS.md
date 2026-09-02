# COMMANDS

Not executed in this packet. Source-backed only.

Reduced session:

```text
uv venv --python 3.12 other
# PYTHONEXECUTABLE points at the default .venv interpreter
PYTHONEXECUTABLE=.venv/bin/python3 uv python find other/bin/python3
env -u PYTHONEXECUTABLE uv python find other/bin/python3
```

Upstream test at the failing revision:

```text
cargo test -p uv --test python python_find_cached_launcher_override -- --exact --nocapture
```

Issue 21062 also used `uv run --no-cache --project <dir> <script>` as a
contrast that avoided the stale interpreter metadata.
