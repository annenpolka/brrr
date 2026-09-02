# OBSERVED

Public python-poetry/poetry#10314 / PR 10987. Failing world around `9b1dfc571c445183f038a0477c881e299729d547`. Poetry 2.1.2 on macOS reported:

Edit `pyproject.toml` to `sqlalchemy[postgresql] @ git+...`, then `poetry lock`:

```
   1: fact: poetry-extra-git depends on sqlalchemy[postgresql] (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: selecting sqlalchemy[postgresql] (2.1.0b1.dev0 4512255)
```

No `psycopg2` fact. Lock is written. `poetry show` lacks the extra’s optional dependency.

Then `poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy` on the same tree:

```
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on sqlalchemy (2.1.0b1.dev0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on typing-extensions (>=4.6.0)
   1: fact: sqlalchemy[postgresql] (2.1.0b1.dev0) depends on psycopg2 (>=2.7)
   1: derived: psycopg2 (>=2.7)
```

`pyproject.toml` is unchanged by that add. The git/VCS case is the one that drops the extra’s dependency on lock-after-edit; the reporter says the PyPI equivalent of the extra-edit-then-lock path includes `psycopg2`.

Relevant failing-revision sketch from `Provider.complete_package` (names only; this is the world, not a prescribed repair):

```python
if dependency.extras:
    stack = sorted(dependency.extras)
    while stack:
        extra = stack.pop()
        extra_dependencies = package.extras.get(extra, [])
        for extra_dependency in extra_dependencies:
            if extra_dependency.name == dependency.name:
                stack += sorted(extra_dependency.extras)
            else:
                optional_dependencies.add(extra_dependency.name)
    ...
for dep in requires:
    ...
```

`package.extras` still maps the extra name onto optional dependency objects. After lock-on-edit, `requires` as used by the extras walk is not enough to grow `psycopg2`.
