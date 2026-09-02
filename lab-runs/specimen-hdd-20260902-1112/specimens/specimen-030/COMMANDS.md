# COMMANDS

Not executed in this packet. Commands as reported against the failing revision.

```bash
git clone https://github.com/pytest-dev/pytest-rerunfailures.git
cd pytest-rerunfailures
git checkout 0440e2158c98187a6ccd283e9c0b65475d1cd620
python -m pip install -e . pytest
```

Save the reproducer as `test_example.py` and run:

```bash
pytest -s test_example.py
```

Plugin internals that run between attempts live in `src/pytest_rerunfailures.py` (`pytest_runtest_protocol`). Cleanup that already exists before another attempt:

- `_remove_cached_results_from_failed_fixtures`
- `_remove_failed_setup_state_from_session`
- subtest report scrubbing
