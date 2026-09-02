# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A project first adds a VCS/git dependency without extras (`sqlalchemy @ git+https://github.com/sqlalchemy/sqlalchemy`). The developer then edits `pyproject.toml` so the same git URL is requested with an extra: `sqlalchemy[postgresql] @ git+...`. `poetry lock` completes. `poetry show` does not list `psycopg2`, which is an optional dependency of that extra.

The same extra spelling via `poetry add sqlalchemy[postgresql]@git+https://github.com/sqlalchemy/sqlalchemy` does not change `pyproject.toml`, but the lock then grows `psycopg2`. The PyPI (non-git) form of the same extra-edit-then-lock path does include `psycopg2`.

The developer wants to know which package object the second lock reused, and which extra edges were actually attached to the solved node.

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

python-poetry/poetry
  src/poetry/puzzle/provider.py
  tests/puzzle/test_provider.py
  tests/puzzle/test_solver.py

RELEVANT MATERIAL

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
