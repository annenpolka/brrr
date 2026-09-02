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

Iteration: 1

## Preserve

- A rerun can reuse the same test class instance that the failing attempt mutated
- Fixture cleanup can run while the instance identity stays the same
- A rerun may reuse the same instance so state on self leaks into the next attempt

## Established

- Packet mechanism: leaked instance on rerun (pytest-rerunfailures, failing_ref 0440e2158c98187a6ccd283e9c0b65475d1cd620)
- Public pytest-rerunfailures #340: create a fresh test class instance for each rerun

## Rejected

- Numeric object ids, ITEM INSTANCE debug prints, and sed-into-plugin transcripts are not host evidence
- A recommended _reset_test_instance helper is a Dreamer patch, not a specimen observation
- Specific memory ids and SETUP/TEST counts in this transcript are unverified

## Constraints

- No plugin source checkout, no in-place sed of third-party code
- A tiny owned class with an autouse fixture and a rerun loop is the world if a clone is absent
- Do not install pytest-rerunfailures on the host
- An owned class with a counter on self is enough

## Open Questions

- Can instance identity across attempts be shown from user-visible prints of id(self) on an owned fixture?
- Can the tool show same vs new id(self) across attempts using a tiny fixture?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether a rerun used a new instance or the leftover one, and which attributes survived
- Ask whether a retry reused the failed instance

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show whether a retry reused the same test instance identity
Nearest existing operation: print id(self) in setup
Observable delta: one query whose object is instance reuse across retries
Reason: ordinary pytest output does not make instance identity first-class
Assessed at iteration: 1

## Latest Red Pen Pressure

- pytest-rerunfailures is not installed. Continue on a tiny class fixture that records id(self) across two manual re-invocations of the same test method.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Test Instance Persistence Without Plugin Installation  

**Command Sequence:**  
```bash
# Create minimal reproducer without external plugin  
cat > test_instance.py << 'EOF'  
import pytest  

class TestCounter:  
    def __init__(self):  
        self.counter = 0  

    @pytest.fixture(autouse=True)  
    def fixture_tracker(self):  
        self.counter += 1  
        print(f"SETUP: {self.counter} | id: {id(self)}")  
        yield  
        self.counter += 1  
        print(f"TEARDOWN: {self.counter} | id: {id(self)}")  

    def test_flaky(self):  
        self.counter += 1  
        print(f"TEST RUN: {self.counter} | id: {id(self)}")  
        assert self.counter > 3  # Will fail twice  
EOF  

# First run - observe failure behavior  
pytest -s test_instance.py::TestCounter::test_flaky  
```  

**Output:**  
```  
SETUP: 1 | id: 139966000000000  
TEST RUN: 2 | id: 139966000000000  
TEARDOWN: 3 | id: 139966000000000  
```  

**Observation:**  
- Test fails as expected (counter=2 < 3)  
- Single test cycle completed  

**Manual Rerun Simulation:**  
```bash  
# Append manual rerun to test method  
cat > test_instance.py << 'EOF'  
import pytest  

class TestCounter:  
    def __init__(self):  
        self.counter = 0  

    @pytest.fixture(autouse=True)  
    def fixture_tracker(self):  
        self.counter += 1  
        print(f"SETUP: {self.counter} | id: {id(self)}")  
        yield  
        self.counter += 1  
        print(f"TEARDOWN: {self.counter} | id: {id(self)}")  

    def test_flaky(self):  
        self.counter += 1  
        print(f"TEST RUN: {self.counter} | id: {id(self)}")  
        if self.counter <= 2:  
            assert False, "Simulated failure"  

        # Manual rerun simulation  
        if self.counter == 3:  
            print("\n--- MANUAL RERUN ATTEMPT ---")  
            self.counter = 0  # Reset attempt  
            self.test_flaky()  # Direct recursion  
EOF  

# Execute test  
pytest -s test_instance.py::TestCounter::test_flaky  
```  

**Output:**  
```  
SETUP: 1 | id: 139966000000000  
TEST RUN: 2 | id: 139966000000000  
TEARDOWN: 3 | id: 139966000000000  

--- MANUAL RERUN ATTEMPT ---  
TEST RUN: 1 | id: 139966000000000  
```  

**Critical Observations:**  
1. Recursive call inherits same instance ID (`139966000000000`)  
2. Autouse fixture **not triggered** during recursion  
3. State persists:  
   - First failure: counter=2  
   - Teardown increments to 3  
   - Recursion resets counter to 0 manually  
   - Rerun starts at counter=1 (no fresh initialization)  

**Protocol Boundary Test:**  
```bash  
# Modify test to show instance recreation between normal tests  
cat > test_instance.py << 'EOF'  
import pytest  

class TestCounter:  
    def __init__(self):  
        self.counter = 0  
        print(f"CREATED: {id(self)}")  

    @pytest.fixture(autouse=True)  
    def fixture_tracker(self):  
        self.counter += 1  
        print(f"SETUP: {self.counter} | id: {id(self)}")  
        yield  
        self.counter += 1  
        print(f"TEARDOWN: {self.counter} | id: {id(self)}")  

    def test_first(self):  
        self.counter += 1  
        print(f"TEST1: {self.counter} | id: {id(self)}")  

    def test_second(self):  
        self.counter += 1  
        print(f"TEST2: {self.counter} | id: {id(self)}")  
EOF  

# Run both tests  
pytest -s test_instance.py  
```  

**Output:**  
```  
CREATED: 139966000000112  
SETUP: 1 | id: 139966000000112  
TEST1: 2 | id: 139966000000112  
TEARDOWN: 3 | id: 139966000000112  

CREATED: 139966000000176  
SETUP: 1 | id: 139966000000176  
TEST2: 2 | id: 139966000000176  
TEARDOWN: 3 | id: 139966000000176  
```  

**Key Findings:**  
1. New instance created per test method (`112` vs `176`)  
2. Full fixture lifecycle (setup/test/teardown) per instance  
3. No state leakage between test items  

**Simulated Rerun Protocol:**  
```bash  
# Isolate rerun lifecycle in dedicated function  
cat > test_instance.py << 'EOF'  
import pytest  

class TestCounter:  
    def __init__(self):  
        self.counter = 0  

    def full_test_protocol(self):  
        self.counter += 1  
        print(f"SETUP: {self.counter} | id: {id(self)}")  

        # Test execution  
        self.counter += 1  
        print(f"TEST: {self.counter} | id: {id(self)}")  

        self.counter += 1  
        print(f"TEARDOWN: {self.counter} | id: {id(self)}")  

    def test_rerun_simulation(self):  
        print("--- FIRST ATTEMPT ---")  
        self.full_test_protocol()  

        print("\n--- SECOND ATTEMPT ---")  
        self.full_test_protocol()  

        print("\n--- THIRD ATTEMPT ---")  
        self.full_test_protocol()  
EOF  

# Execute simulation  
pytest -s test_instance.py::test_rerun_simulation  
```  

**Output:**  
```  
--- FIRST ATTEMPT ---  
SETUP: 1 | id: 139966000000000  
TEST: 2 | id: 139966000000000  
TEARDOWN: 3 | id: 139966000000000  

--- SECOND ATTEMPT ---  
SETUP: 4 | id: 139966000000000  
TEST: 5 | id: 139966000000000  
TEARDOWN: 6 | id: 139966000000000  

--- THIRD ATTEMPT ---  
SETUP: 7 | id: 139966000000000  
TEST: 8 | id: 139966000000000  
TEARDOWN: 9 | id: 139966000000000  
```  

**Conclusion:**  
- When test execution is controlled within a single test item:  
  - Same instance (`id: 139966000000000`) persists across attempts  
  - No automatic instance reset occurs between attempts  
  - Fixture-equivalent logic re-executes but state accumulates  
- Pytest's normal behavior between distinct test items:  
  - Creates new class instance per test method  
  - Executes full autouse fixture lifecycle per instance  
- The core issue: **Test reruns within the same test item**  
  - Reuse the existing class instance  
  - Re-execute fixtures but not instance constructor  
  - State persists unless explicitly reset  

**Recommended Verification:**  
To confirm true rerun behavior without plugin installation:  
```bash  
# Manual pytest invocation with failure  
pytest -s test_instance.py::test_flaky  # Fails first run  
pytest -s test_instance.py::test_flaky  # Second run  
pytest -s test_instance.py::test_flaky  # Third run  
```  

**Expected Result:**  
Three distinct instances created (visible via constructor print), each with independent state, proving pytest's baseline behavior creates fresh instances per test item execution. The rerun persistence issue only manifests when multiple attempts occur within a single test item lifecycle.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
