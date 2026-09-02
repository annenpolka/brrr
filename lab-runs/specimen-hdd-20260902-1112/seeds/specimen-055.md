CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

pytest is invoked with `--rootdir proj` while collection starts at the parent directory that contains both `proj/` and `tests/`. A name injected by `proj/conftest.py` is missing for the collected test. Collecting only under `proj/` the name is present.

The developer wants to know which conftest/config objects actually applied to the collected item.

# OBSERVED

Owned layout (not a pytest clone):

```
parent/
  tests/test_item.py
  proj/conftest.py   # defines helper = 'from-rootdir-conftest'
  proj/pytest.ini
```

Host-captured idea: a test that prints `helper if present else 'MISSING'`.

When the collection path is the parent, the item can run without the rootdir conftest binding. When collection is inside `proj/`, the binding is present.

This packet does not execute pytest 9.1.1 on the host; it is a reduced layout of specimen-002.

# COMMANDS

```
# conceptual:
# pytest --rootdir=proj tests/test_item.py
# pytest --rootdir=proj proj
```

parent
  tests/test_item.py
  proj/conftest.py
  proj/pytest.ini

RELEVANT MATERIAL

### proj/conftest.py

helper = 'from-rootdir-conftest'

### proj/pytest.ini

[pytest]

### tests/test_item.py

def test_item():
    try:
        print('helper', helper)
    except NameError:
        print('helper', 'MISSING')

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
