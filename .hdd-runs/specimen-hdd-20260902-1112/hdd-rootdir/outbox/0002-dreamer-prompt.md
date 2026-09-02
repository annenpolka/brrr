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

A project runs pytest with `--rootdir` pointing at a *subdirectory* and collects tests/doctests from a *parent* path. Names injected via the rootdir conftest (including `doctest_namespace`) are missing: doctests fail `NameError`.

The same layout passed on pytest 9.0.3 and fails on 9.1.1.

The developer needs to see *which configuration objects actually apply* to the collected items, not a guess about versions.

# OBSERVED

Reporter invocation (xclim):

```
pytest --rootdir src/xclim/testing --config-file=src/xclim/testing/conftest.py \
       --doctest-modules src/xclim
```

- pytest 9.0.3: pass
- pytest 9.1.1: `NameError: name '...' is not defined` for names the rootdir conftest meant to inject

Public issue pytest-dev/pytest#14683 / PR 14694.

# COMMANDS

```
pytest --rootdir <subdir> --config-file=<subdir>/conftest.py --doctest-modules <parent>
```

src/xclim/testing/conftest.py
src/xclim/  (modules collected from parent of rootdir)

RELEVANT MATERIAL

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

# Previous field report

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

## Behavior already demonstrated

- rootdir in a subdirectory plus collection from a parent can drop names the rootdir conftest meant to inject
- Packet: pytest 9.0.3 pass vs 9.1.1 NameError on the reporter invocation


## Newly confirmed limits and corrections

- No xclim checkout
- A tiny directory layout with rootdir-subdir vs parent collection is the world


## Current operator request

- There is no xclim tree. Continue using a two-directory fixture: conftest in a subdirectory rootdir, items collected from a parent path. Show which config applied to which item.


## New information since the previous report

- There is no xclim tree. Continue using a two-directory fixture: conftest in subdir rootdir, tests collected from parent. Show which config applied to which item.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
