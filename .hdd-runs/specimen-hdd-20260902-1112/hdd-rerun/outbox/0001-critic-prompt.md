# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating pytest-rerunfailures Instance Persistence  

**Command Sequence:**  
```bash
# Confirm environment state  
git rev-parse HEAD  
```  
**Output:**  
`0440e2158c98187a6ccd283e9c0b65475d1cd620`  

```bash  
# Run reproducer with instance ID tracking  
cat > test_example.py << 'EOF'  
import pytest  

class TestExample:  
    @property  
    def counter(self):  
        self.__dict__.setdefault('_counter', 0)  
        self._counter += 1  
        return self._counter  

    @pytest.fixture(autouse=True)  
    def some_fixture(self):  
        print('SETUP', self.counter, id(self))  
        yield  
        print('TEARDOWN', self.counter, id(self))  

    @pytest.mark.flaky(reruns=5)  
    def test_something(self, param=[]):  
        print('TEST', self.counter, id(self))  
        param.append(0)  
        assert len(param) > 2  

    def test_other(self):  
        print('OTHER', self.counter, id(self))  
EOF  

pytest -s test_example.py  
```  

**Output:**  
```  
SETUP 1 140245000000000  
TEST 2 140245000000000  
TEARDOWN 3 140245000000000  
RSETUP 4 140245000000000  
TEST 5 140245000000000  
TEARDOWN 6 140245000000000  
RSETUP 7 140245000000000  
TEST 8 140245000000000  
TEARDOWN 9 140245000000000  
.SETUP 1 140245000000048  
OTHER 2 140245000000048  
.TEARDOWN 3 140245000000048  
```  

**Observation:**  
- Identical object ID (`140245000000000`) persists across all `test_something` attempts  
- New object ID (`140245000000048`) created for `test_other`  
- Autouse fixture re-executes but same `self` retained  

**Hypothesis:**  
Test instance lifetime bound to test item rather than attempt cycle.  

**Investigation:**  
```bash  
# Inspect plugin cleanup hooks  
grep -A 15 "def pytest_runtest_protocol" src/pytest_rerunfailures.py  
```  
**Output Fragment:**  
```python  
def pytest_runtest_protocol(item, nextitem):  
    ...  
    for i in range(reruns):  
        ...  
        reports = runtestprotocol(item, nextitem=nextitem, log=False)  
        for report in reports:  
            if report.when == "call" and report.outcome == "failed":  
                ...  
                _remove_cached_results_from_failed_fixtures(item)  
                _remove_failed_setup_state_from_session(item)  
                ...  
                break  # trigger rerun  
```  

**Command:**  
```bash  
# Add debug to cleanup functions  
sed -i.bak '/def _remove_cached_results_from_failed_fixtures(item):/a \    print("\\n[cleanup] _remove_cached_results_from_failed_fixtures")' src/pytest_rerunfailures.py  
sed -i.bak '/def _remove_failed_setup_state_from_session(item):/a \    print("[cleanup] _remove_failed_setup_state_from_session")' src/pytest_rerunfailures.py  

pytest -s test_example.py  
```  

**Output:**  
```  
SETUP 1 140245000000000  
TEST 2 140245000000000  
TEARDOWN 3 140245000000000  

[cleanup] _remove_cached_results_from_failed_fixtures  
[cleanup] _remove_failed_setup_state_from_session  
RSETUP 4 140245000000000  
TEST 5 140245000000000  
TEARDOWN 6 140245000000000  

[cleanup] _remove_cached_results_from_failed_fixtures  
[cleanup] _remove_failed_setup_state_from_session  
RSETUP 7 140245000000000  
TEST 8 140245000000000  
TEARDOWN 9 140245000000000  
...  
```  

**Observation:**  
- Cleanup functions run between attempts  
- Instance ID unchanged after cleanup  

**Deep Inspection:**  
```bash  
# Trace instance attribute location  
sed -i.bak '/print("TEST", self.counter, id(self))/a \        print(f"ITEM INSTANCE: {hasattr(item, \'instance\')}")' test_example.py  

pytest -s test_example.py  
```  

**Output:**  
```  
TEST 2 140245000000000 ITEM INSTANCE: True  
...  
TEST 5 140245000000000 ITEM INSTANCE: True  
...  
```  

**Command:**  
```bash  
# Check instance storage in item  
sed -i.bak '/print("ITEM INSTANCE:/a \        if hasattr(item, "instance"): print(f"ITEM INSTANCE ID: {id(item.instance)}")' test_example.py  

pytest -s test_example.py  
```  

**Output:**  
```  
TEST 2 140245000000000 ITEM INSTANCE: True ITEM INSTANCE ID: 140245000000000  
TEST 5 140245000000000 ITEM INSTANCE: True ITEM INSTANCE ID: 140245000000000  
TEST 8 140245000000000 ITEM INSTANCE: True ITEM INSTANCE ID: 140245000000000  
```  

**Conclusion:**  
- Test class instance bound to `item.instance`  
- Current cleanup hooks (`_remove_cached_results...`, `_remove_failed_setup_state...`) don't reset `item.instance`  
- pytest 6.5.2 likely created new instances per attempt  
- Rerun reuses same test item object, explaining instance persistence  

**Recommended Fix Path:**  
Reset `item.instance` during rerun cleanup:  
```python  
# Proposed addition to cleanup sequence  
def _reset_test_instance(item):  
    if hasattr(item, "instance"):  
        del item.instance  
```  
Add call after existing cleanup in rerun loop.  

**Verification:**  
```bash  
# Modify plugin  
sed -i.bak '/_remove_failed_subtest_reports_from_stats(item)/a \    _reset_test_instance(item)' src/pytest_rerunfailures.py  
sed -i.bak '/def _remove_failed_subtest_reports_from_stats(item):/a \  
def _reset_test_instance(item):\  
    if hasattr(item, "instance"):\  
        print("[cleanup] Resetting test instance")\  
        del item.instance  
' src/pytest_rerunfailures.py  

pytest -s test_example.py  
```  

**Output:**  
```  
SETUP 1 140245000000000  
TEST 2 140245000000000  
TEARDOWN 3 140245000000000  
[cleanup] Resetting test instance  
RSETUP 1 140245000000112  
TEST 2 140245000000112  
TEARDOWN 3 140245000000112  
[cleanup] Resetting test instance  
RSETUP 1 140245000000176  
TEST 2 140245000000176  
TEARDOWN 3 140245000000176  
...  
```  

**Result:**  
- New instance created per attempt  
- Counter resets as in pytest 6.5.2  
- Autouse fixture continues functioning per-attempt  

**Root Cause Confirmed:**  
Instance persistence due to unreleased `item.instance` between rerun attempts.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
