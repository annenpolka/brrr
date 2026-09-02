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
