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
Two scripts. A: `true && echo ok` step status 0, all commands 0. B: `false || echo ok` step status 0, first command 1. Only observed difference is whether a nonzero was swallowed.

# OBSERVED
See files/a.sh and files/b.sh. Captured:

bash files/a.sh; echo A:$?
bash files/b.sh; echo B:$?

files/a.sh
files/b.sh

RELEVANT MATERIAL

### a.sh

true && echo ok

### b.sh

false || echo ok

### nested_pyproject.toml

# pip-26.2.1/build-project/pyproject.toml — no [build-system]
[project]
name = "build-project-helper"

### read_pyproject_failing.py

# Reduced excerpt of _read_pyproject on failing_ref
# setuptools/tests/integration/test_pip_install_sdist.py

def _read_pyproject(archive):
    contents = (
        archive.get_content(member)
        for member in archive
        if os.path.basename(archive.get_name(member)) == "pyproject.toml"
    )
    return next(contents, "")

### root_pyproject.toml

# pip-26.2.1/pyproject.toml
[build-system]
requires = ["flit-core >=3.11,<4"]
build-backend = "flit_core.buildapi"

### sdist_members.txt

pip-26.2.1 sdist member order (relevant names only):
pip-26.2.1/build-project/pyproject.toml
pip-26.2.1/pyproject.toml

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
