# OBSERVED

Reporter invocation (xclim):

```
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim
```

- pytest 9.0.3: pass
- pytest 9.1.1: `NameError: name '...' is not defined` for names the rootdir conftest meant to inject

Public issue pytest-dev/pytest#14683 / PR 14694.
