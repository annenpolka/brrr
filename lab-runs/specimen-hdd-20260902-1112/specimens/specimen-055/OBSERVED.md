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
