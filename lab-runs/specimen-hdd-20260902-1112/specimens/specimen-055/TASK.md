# TASK

pytest is invoked with `--rootdir proj` while collection starts at the parent directory that contains both `proj/` and `tests/`. A name injected by `proj/conftest.py` is missing for the collected test. Collecting only under `proj/` the name is present.

The developer wants to know which conftest/config objects actually applied to the collected item.
