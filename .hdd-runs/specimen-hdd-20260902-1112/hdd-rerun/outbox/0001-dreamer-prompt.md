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

A checkout of pytest-rerunfailures sits at 0440e2158c98187a6ccd283e9c0b65475d1cd620.

The plugin re-runs a failed test item up to N times. A class-based test is marked `@pytest.mark.flaky(reruns=5)`. An autouse fixture and the test body both write to `self`. Pytest otherwise gives each test item its own class instance.

The developer is trying to understand why a rerun of the same test method does not start from a clean `self`, while a later sibling method in the same class does.

Outcome sought: determine what is shared across attempts of one item, what is reset, and what a rerun of a class method actually reuses.

# OBSERVED

Reporter used pytest>=7.0.0 with pytest-rerunfailures. Same file on pytest 6.5.2 produced a fresh `self` on each attempt.

Reproducer (issue 268):

```python
import pytest

class TestExample:
    @property
    def counter(self):
        self.__dict__.setdefault('_counter', 0)
        self._counter += 1
        return self._counter

    @pytest.fixture(autouse=True)
    def some_fixture(self):
        print('SETUP', self.counter)
        yield
        print('TEARDOWN', self.counter)

    @pytest.mark.flaky(reruns=5)
    def test_something(self, param=[]):
        print('TEST', self.counter)
        param.append(0)
        assert len(param) > 2

    def test_other(self):
        print('OTHER', self.counter)
```

Command: `pytest -s test_example.py`

Observed stdout (pytest>=7):

```
SETUP 1
TEST 2
TEARDOWN 3
RSETUP 4
TEST 5
TEARDOWN 6
RSETUP 7
TEST 8
TEARDOWN 9
.SETUP 1
OTHER 2
.TEARDOWN 3
```

Paired contrast:

- Attempts of `test_something` keep incrementing one counter: 1..9 then pass on the third try.
- `test_other` then starts again at SETUP 1.
- On pytest 6.5.2 the rerun block of `test_something` also restarted at 1.

A second shape: state set on `self` during a failed attempt is still present on the next attempt (`hasattr(self, 'seen_by_test')` is True). Function-scoped fixtures do re-run (SETUP/TEARDOWN print on every attempt). Class/module/session fixtures are not supposed to re-run on a rerun.

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

TREE (failing checkout fragment)

pytest-rerunfailures/                    # 0440e2158c98187a6ccd283e9c0b65475d1cd620
├── src/
│   └── pytest_rerunfailures.py          # pytest_runtest_protocol rerun loop
└── tests/
    └── test_pytest_rerunfailures.py

Working file used to inhabit the failure:

test_example.py                          # class + flaky marker + autouse fixture

RELEVANT MATERIAL

### src/pytest_rerunfailures.py.fragment

# failing_ref 0440e2158c98187a6ccd283e9c0b65475d1cd620
# excerpts from src/pytest_rerunfailures.py

def _remove_cached_results_from_failed_fixtures(item):
    cached_result = "cached_result"
    fixture_info = getattr(item, "_fixtureinfo", None)
    for fixture_def_str in getattr(fixture_info, "name2fixturedefs", ()):
        fixture_defs = fixture_info.name2fixturedefs[fixture_def_str]
        for fixture_def in fixture_defs:
            if getattr(fixture_def, cached_result, None) is not None:
                result, _, err = getattr(fixture_def, cached_result)
                if err:
                    setattr(fixture_def, cached_result, None)
                    if hasattr(fixture_def, "_finalizers"):
                        fixture_def._finalizers.clear()


def _remove_failed_setup_state_from_session(item):
    setup_state = item.session._setupstate
    if item in setup_state.stack:
        del setup_state.stack[item]


# inside pytest_runtest_protocol, after a failed attempt that will be retried:
                report.outcome = "rerun"
                time.sleep(delay * delay_backoff_factor ** (item.execution_count - 1))
                if not parallel or works_with_current_xdist():
                    item.ihook.pytest_runtest_logreport(report=report)
                _remove_cached_results_from_failed_fixtures(item)
                _remove_failed_setup_state_from_session(item)
                _remove_failed_subtests_from_report(item, report)
                _remove_failed_subtest_reports_from_stats(item)
                break  # trigger rerun

### test_example.py

import pytest

class TestExample:
    @property
    def counter(self):
        self.__dict__.setdefault("_counter", 0)
        self._counter += 1
        return self._counter

    @pytest.fixture(autouse=True)
    def some_fixture(self):
        print("SETUP", self.counter)
        yield
        print("TEARDOWN", self.counter)

    @pytest.mark.flaky(reruns=5)
    def test_something(self, param=[]):
        print("TEST", self.counter)
        param.append(0)
        assert len(param) > 2

    def test_other(self):
        print("OTHER", self.counter)

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
