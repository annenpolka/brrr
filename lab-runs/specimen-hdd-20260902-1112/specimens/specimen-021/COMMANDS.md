# COMMANDS

Public reproduction from the issue (not run on this host):

```
poetry new poetry-extra-git
poetry add sqlalchemy@git+https://github.com/sqlalchemy/sqlalchemy
# edit pyproject.toml: sqlalchemy → sqlalchemy[postgresql] at the same git URL
poetry lock
poetry show
poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy
poetry show
```

This packet does not include a local clone; treat the issue logs and the `complete_package` sketch as the world.
