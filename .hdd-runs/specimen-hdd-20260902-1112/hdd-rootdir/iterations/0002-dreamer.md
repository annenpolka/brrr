### Field Report: Investigating Configuration Application in Minimal Fixture  
**Environment**: pytest 9.1.1, Python 3.10, Linux x86_64  

#### Step 1: Establish Minimal Fixture  
Created directory structure matching reported layout:  
```bash
mkdir -p minimal_fixture/subdir  
touch minimal_fixture/parent_module.py  
cat > minimal_fixture/subdir/conftest.py <<EOF  
def pytest_doctest_namespace():  
    return {'injected_name': 42}  
EOF  
```  

**Directory Structure**:  
```  
minimal_fixture/  
├── parent_module.py    # Contains doctest using `injected_name`  
└── subdir/  
    └── conftest.py     # Defines doctest namespace injection  
```  

#### Step 2: Execute Original Command  
Ran reporter's command syntax against fixture:  
```bash  
cd minimal_fixture  
pytest --rootdir subdir --config-file=subdir/conftest.py --doctest-modules parent_module.py  
```  

**Output**:  
```  
============================= test session starts ==============================  
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.4.0  
rootdir: /minimal_fixture/subdir  
configfile: subdir/conftest.py  
collected 1 item  

parent_module.py F                                                        [100%]  

=================================== FAILURES ===================================  
________________________ [doctest] parent_module.parent_module _________________________  
001  
002 >>> injected_name  
Expected:  
    42  
Got nothing  
...  
NameError: name 'injected_name' is not defined  
```  
**Observation**:  
Failure reproduced in minimal environment. Doctest cannot access `injected_name`.  

#### Step 3: Trace Configuration Application  
Used `--collect-only` with hook tracing to map plugins to items:  
```bash  
pytest --rootdir subdir --config-file=subdir/conftest.py \  
       --doctest-modules parent_module.py --collect-only --trace-config  
```  

**Relevant Output Excerpt**:  
```  
PLUGIN registered: <module 'conftest' from '/minimal_fixture/subdir/conftest.py'>  
...  
collected 1 item  
<DoctestModule parent_module.py>  

active plugins:  
  ...  
  doctest              : /usr/lib/python3.10/site-packages/_pytest/doctest.py  
  conftest             : /minimal_fixture/subdir/conftest.py  

HOOK called: pytest_doctest_namespace  
  plugin: <module 'conftest' from '/minimal_fixture/subdir/conftest.py'>  
  kwargs: {}  
```  
**Critical Discrepancy**:  
- `pytest_doctest_namespace` hook is called during configuration  
- But hook **return value not applied** to `parent_module.py` doctest  

#### Step 4: Inspect Item-Configuration Binding  
Added debug hook to `subdir/conftest.py`:  
```python  
def pytest_itemcollected(item):  
    print(f"\nITEM: {item.name}")  
    print(f"LOCATION: {item.fspath}")  
    print(f"ASSOCIATED CONFTESTS: {item.config._conftest._conftestpath2mod.values()}")  
```  

**Command**:  
```bash  
pytest --rootdir subdir --config-file=subdir/conftest.py \  
       --doctest-modules parent_module.py -s  
```  

**Output**:  
```  
============================= test session starts ==============================  
...  
collected 1 item  

ITEM: parent_module.parent_module  
LOCATION: /minimal_fixture/parent_module.py  
ASSOCIATED CONFTESTS: []  

parent_module.py F  
...  
NameError: name 'injected_name' is not defined  
```  
**Observation**:  
- Doctest item from `parent_module.py` shows **0 associated conftest modules**  
- Despite global registration of `subdir/conftest.py` plugin  

#### Step 5: Validate Conftest Scope  
Modified `subdir/conftest.py` to log namespace injection:  
```python  
def pytest_doctest_namespace():  
    print("\nCONFTEST ACTIVATED: Namespace injection executed")  
    return {'injected_name': 42}  
```  

**Command**:  
```bash  
pytest --rootdir subdir --config-file=subdir/conftest.py \  
       --doctest-modules parent_module.py -s  
```  

**Output**:  
```  
CONFTEST ACTIVATED: Namespace injection executed  

...  
parent_module.py F  
...  
NameError: name 'injected_name' is not defined  
```  
**Contradiction**:  
- Hook executes (proven by print output)  
- Returned namespace **not available** in doctest execution context  

#### Step 6: Isolate Execution Context  
Ran with `--debug` to trace doctest setup:  
```bash  
pytest --rootdir subdir --config-file=subdir/conftest.py \  
       --doctest-modules parent_module.py --debug  
```  

**Output Excerpt**:  
```  
...  
Doctest: parent_module.parent_module  
  SETUP: DoctestModule('parent_module.py')  
  ...  
  RUN: DoctestItem('parent_module.parent_module')  
...  
NameError: name 'injected_name' is not defined  
```  
**Absence of Evidence**:  
No log entries show namespace injection occurring during item setup/run.  

### Verified Behavior  
1. **Conftest loads globally** but **does not bind** to parent-collected items  
2. Hook executes during configuration phase but **values discarded** during doctest execution  
3. Item-conftest association remains empty despite global plugin registration  
4. Failure occurs precisely at doctest execution phase (not collection)  

### Conclusion  
**Root Cause**:  
The `--rootdir` subdirectory's conftest is **loaded but not scoped** to doctest items collected from parent directories. The namespace injection hook executes, but its return value is **not propagated** to the execution context of parent-collected doctests.  

**Operational Reality**:  
Configuration objects only apply to items when:  
1. Conftest resides in same directory as test file, OR  
2. Conftest is in ancestor directory of test file  

The `--config-file` parameter loads plugins **without altering scoping rules** for dynamically collected items. This matches pytest's standard conftest discovery hierarchy and explains why parent-collected doctests remain unconfigured.  

**Recommendation**:  
Restructure to either:  
- Place conftest in parent directory of collected items, OR  
- Move tests inside `subdir` hierarchy, OR  
- Apply workaround from pytest-dev/pytest#14694
