# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A project runs pytest with `--rootdir` pointing at a *subdirectory* and collects tests/doctests from a *parent* path. Names injected via the rootdir conftest (including `doctest_namespace`) are missing: doctests fail `NameError`.

The same layout passed on pytest 9.0.3 and fails on 9.1.1.

The developer needs to see *which configuration objects actually apply* to the collected items, not a guess about versions.

# OBSERVED

Reporter invocation (xclim):

```
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim
```

- pytest 9.0.3: pass
- pytest 9.1.1: `NameError: name '...' is not defined` for names the rootdir conftest meant to inject

Public issue pytest-dev/pytest#14683 / PR 14694.

# COMMANDS

```
pytest --rootdir <subdir> --config-file=<subdir>/conftest.py --doctest-modules <parent>
```

src/xclim/testing/conftest.py
src/xclim/  (modules collected from parent of rootdir)

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
