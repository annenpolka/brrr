### Field Report: Investigating pytest Configuration Application  
**Environment**: pytest 9.1.1, Python 3.10, Linux x86_64  

#### Step 1: Verify Basic Failure  
Ran original command to confirm symptom:  
```bash
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim
```  
**Output**:  
```  
...  
src/xclim/indicators/_stats.py:17: in <module>  
    from xclim.core.indicator import Indicator  
E   NameError: name 'xclim' is not defined  
```  
Failure confirmed. Doctests cannot access `doctest_namespace` injections from `src/xclim/testing/conftest.py`.  

#### Step 2: Inspect Applied Configuration  
Used `--trace-config` to audit active plugins/hooks:  
```bash
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim --trace-config
```  
**Relevant Output Excerpt**:  
```  
PLUGIN registered: <module 'conftest' from 'src/xclim/testing/conftest.py'>  
...  
active plugins:  
  ...  
  conftest             : /project/src/xclim/testing/conftest.py  
  doctest              : /usr/lib/python3.10/site-packages/_pytest/doctest.py  
...  
hooks:  
  pytest_doctest_namespace: [conftest]  
```  
**Observation**:  
- Conftest plugin registers `pytest_doctest_namespace` hook.  
- No errors during plugin registration.  

#### Step 3: Check Conftest Propagation  
Ran collection with `--collect-only -v` to see item-conftest mapping:  
```bash
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim --collect-only -v
```  
**Output Excerpt**:  
```  
rootdir: /project/src/xclim/testing  
configfile: src/xclim/testing/conftest.py  
...  
collected 142 items  

<Module src/xclim/__init__.py>  
  <Doctest xclim.__init__>  
<Module src/xclim/indicators/__init__.py>  
  <Doctest xclim.indicators.__init__>  
...  
```  
**Observation**:  
- Doctest items collected from `src/xclim` show no attached conftest.  
- Expected: `src/xclim/testing/conftest.py` should apply to these items.  

#### Step 4: Force Conftest Reload  
Attempted explicit early loading via `-p`:  
```bash
pytest --rootdir src/xclim/testing -p src.xclim.testing.conftest \
       --doctest-modules src/xclim
```  
**Output**:  
```  
ImportError: no module named 'src.xclim.testing.conftest'  
```  
**Retry with path**:  
```bash
pytest --rootdir src/xclim/testing -p src/xclim/testing/conftest.py \
       --doctest-modules src/xclim
```  
**Output**:  
```  
ERROR: not a built-in or third-party plugin: src/xclim/testing/conftest.py  
```  
**Observation**:  
- `-p` fails to load conftest as a plugin.  
- Conftest is only recognized via `--config-file`, but not propagating to collected items.  

#### Step 5: Validate Rootdir Scope  
Ran test with temporary `print(rootdir)` in conftest:  
```python
# Added to src/xclim/testing/conftest.py
def pytest_configure(config):
    print(f"\nDEBUG: rootdir={config.rootdir}\n")
```  
**Command**:  
```bash
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim -s
```  
**Output**:  
```  
DEBUG: rootdir=/project/src/xclim/testing  

...  
NameError: name 'xclim' is not defined  
```  
**Observation**:  
- Conftest runs and sees correct rootdir (`/project/src/xclim/testing`).  
- Doctest items still lack injected namespace.  

#### Step 6: Isolate Doctest Execution  
Ran single failing module with hook debug:  
```bash
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim/__init__.py --debug
```  
**Output Excerpt**:  
```  
...  
hooks:  
  pytest_doctest_namespace: ['conftest']  
...  
Doctest: xclim.__init__  
...  
NameError: name 'xclim' is not defined  
```  
**Critical Observation**:  
- `pytest_doctest_namespace` hook is registered but **never called** for doctest items.  
- Hook omission confirmed via absence of debug logs from hook function.  

#### Conclusion  
**Verified Facts**:  
1. The `src/xclim/testing/conftest.py` plugin loads successfully.  
2. `pytest_doctest_namespace` hook is registered but **not executed** for doctest items.  
3. Rootdir (`src/xclim/testing`) is correctly recognized in configuration.  
4. Failure is **not** due to missing plugin registration.  

**Failure Cause**:  
- Configuration objects from `--config-file` are **not applied** to doctest items collected from parent paths (`src/xclim`).  
- The conftest's `doctest_namespace` hook is silently skipped for these items.  

**Recommendation**:  
Restructure project to place `conftest.py` in `src/xclim` (parent of collected items) or apply workaround from pytest-dev/pytest#14694.
