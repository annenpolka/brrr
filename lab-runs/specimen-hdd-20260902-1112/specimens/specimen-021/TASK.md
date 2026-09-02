# TASK

A project first adds a VCS/git dependency without extras (`sqlalchemy @ git+https://github.com/sqlalchemy/sqlalchemy`). The developer then edits `pyproject.toml` so the same git URL is requested with an extra: `sqlalchemy[postgresql] @ git+...`. `poetry lock` completes. `poetry show` does not list `psycopg2`, which is an optional dependency of that extra.

The same extra spelling via `poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy` does not change `pyproject.toml`, but the lock then grows `psycopg2`. The PyPI (non-git) form of the same extra-edit-then-lock path does include `psycopg2`.

The developer wants to know which package object the second lock reused, and which extra edges were actually attached to the solved node.
