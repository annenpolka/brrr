# TASK

A project runs pytest with `--rootdir` pointing at a *subdirectory* and collects tests/doctests from a *parent* path. Names injected via the rootdir conftest (including `doctest_namespace`) are missing: doctests fail `NameError`.

The same layout passed on pytest 9.0.3 and fails on 9.1.1.

The developer needs to see *which configuration objects actually apply* to the collected items, not a guess about versions.
