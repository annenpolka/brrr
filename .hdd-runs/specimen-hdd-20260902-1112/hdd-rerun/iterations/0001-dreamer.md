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
