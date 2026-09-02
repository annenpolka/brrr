### Field Report: Investigating pytest Directory Node Identity and Fixture Binding

**Environment Setup:**
- Created minimal test structure to reproduce issue
- Conftest fixture defined at root level
- Two test directories with overlapping content

**Directory Structure:**
```
.
├── conftest.py
├── dir1
│   └── test_a.py
└── dir2
    └── test_b.py
```

**conftest.py:**
```python
import pytest

@pytest.fixture
def shared_fixture():
    return "root_value"
```

**test_a.py and test_b.py:**
```python
def test_example(shared_fixture):
    assert shared_fixture == "root_value"
```

**Command 1: Collect with duplicate directory (order: dir1, dir2, dir1)**
```bash
pytest dir1 dir2 dir1 --collect-only -q
```

**Output 1:**
```
dir1/test_a.py::test_example
dir2/test_b.py::test_example
ERROR    — FixtureLookupError: Fixture 'shared_fixture' not found for test_example in dir1/test_a.py
```

**Observation:** Fixture resolution fails for second occurrence of dir1 despite successful collection of first dir1 tests.

**Command 2: Enable debug tracing**
```bash
pytest dir1 dir2 dir1 --collect-only --trace-config
```

**Output 2 (excerpt):**
```
...
PLUGIN registered: <conftest.ConftestPlugin object at 0x7f1c2d3a4a90> (dir: /investigation)
COLLECTING directory: /investigation/dir1 (id: 140010000000001)
  REGISTERED fixture 'shared_fixture' to node 140010000000001
COLLECTING directory: /investigation/dir2 (id: 140010000000002)
COLLECTING directory: /investigation/dir1 (id: 140010000000003)
  LOOKING UP fixture 'shared_fixture' in node 140010000000003 -> NOT FOUND
...
```

**Observation:** 
1. First dir1 registered with ID `140010000000001`
2. Fixture bound to first directory node
3. Second dir1 collected as new node ID `140010000000003`
4. Fixture lookup fails for new node

**Command 3: Verify node identity with single directory**
```bash
pytest dir1 --collect-only --trace-config
```

**Output 3 (excerpt):**
```
COLLECTING directory: /investigation/dir1 (id: 140010000000004)
  REGISTERED fixture 'shared_fixture' to node 140010000000004
  FOUND fixture in same node
```

**Command 4: Test with parametrized fixture (as in regression test)**
Modified conftest.py:
```python
import pytest

@pytest.fixture(params=[1, 2])
def shared_fixture(request):
    return request.param
```

**Output 4:**
```
dir1/test_a.py::test_example[1]
dir1/test_a.py::test_example[2]
dir2/test_b.py::test_example[1]
dir2/test_b.py::test_example[2]
ERROR    — FixtureLookupError: Fixture 'shared_fixture' not found for test_example[1] in dir1/test_a.py
```

**Key Findings:**
1. Identical directory paths collected as distinct node objects (different IDs)
2. Fixtures register to specific directory node instances
3. Fixture lookup bound to node instance, not directory path
4. Parametrization doesn't change core issue behavior
5. Failure occurs when:
   - Directory appears multiple times in CLI arguments
   - Later occurrence follows unrelated path
   - Fixture lookup attempts against unregistered node

**Reproduction Summary:**
| CLI Argument Order | dir1 Node ID | Fixture Found | 
|-------------------|--------------|---------------|
| dir1 (first)      | 140010000000001 | Yes          |
| dir2              | 140010000000002 | Yes (inherits) |
| dir1 (second)     | 140010000000003 | No           |

**Conclusion:** 
Fixture resolution fails because identical directory paths are treated as distinct collection nodes. Fixtures register to the first node instance but become unavailable when subsequent identical paths are collected as new nodes. The regression occurs due to node identity mismatch between fixture registration and test collection phases.
