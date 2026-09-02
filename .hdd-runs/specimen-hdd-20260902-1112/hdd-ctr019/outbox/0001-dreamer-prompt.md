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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
