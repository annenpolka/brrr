# TASK

Two virtual environments exist:

- `.venv` — the test context default
- `other/` — a second venv created with the same Python version

`uv python find` is asked for `other/bin/python3`.

First invocation sets `PYTHONEXECUTABLE` to `.venv/bin/python3`. The
requested interpreter, under that environment variable, reports the
`.venv` executable.

Second invocation asks for the same `other/bin/python3` path with
`PYTHONEXECUTABLE` *removed*. The developer wants this to print
`other/bin/python3`, not the default `.venv`.
