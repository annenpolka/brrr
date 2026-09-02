# OBSERVED

Owned fixture files/override_subst.py. File-backed template expands. The override path keeps the token as a literal argv element and still reports exit 0.

Public grounding (not executed here): tox-dev/tox#4047 / PR 4048 — `tox -x 'env_run_base.commands=pytest {posargs}' -- tests src` ran pytest against a directory named `{posargs}` rather than forwarding the arguments.

## Captured host execution (stdlib, no third-party packages)
```
file_argv ['pytest', 'tests', 'src']
override_argv ['pytest', '{posargs}']
cli_leftover ['tests', 'src']
override_exit 0
override_ran_against {posargs}
```
