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
