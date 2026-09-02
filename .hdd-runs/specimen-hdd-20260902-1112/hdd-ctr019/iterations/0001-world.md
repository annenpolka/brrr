# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A file-backed command template is `pytest {posargs}`. A CLI override supplies the same spelling, `pytest {posargs}`, plus leftover arguments `tests src`. The process exits 0. One argv actually contains `tests` and `src`. The other argv’s last token is the characters `{posargs}`.

The developer wants to know which layer expanded the token, and which tests (if any) the override actually ran.

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

# COMMANDS

```
python3 files/override_subst.py
```

files/override_subst.py

RELEVANT MATERIAL

### override_subst.py


#!/usr/bin/env python3
def subst(template: str, posargs: list[str]) -> str:
    return template.replace("{posargs}", " ".join(posargs))

def main() -> None:
    file_template = "pytest {posargs}"
    posargs = ["tests", "src"]
    file_cmd = subst(file_template, posargs)
    override = "pytest {posargs}"
    file_argv = file_cmd.split()
    override_argv = override.split()
    print("file_argv", file_argv)
    print("override_argv", override_argv)
    print("cli_leftover", posargs)
    print("override_exit", 0)
    print("override_ran_against", override_argv[-1])

if __name__ == "__main__":
    main()

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
