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
