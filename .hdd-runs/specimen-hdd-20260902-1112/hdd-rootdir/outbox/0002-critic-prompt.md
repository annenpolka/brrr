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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- rootdir in a subdirectory plus collection from a parent can drop names the rootdir conftest meant to inject

## Established

- Packet: pytest 9.0.3 pass vs 9.1.1 NameError on the reporter invocation

## Rejected

- Specific xclim indicator NameError and --trace-config plugin lists are Dreamer-generated

## Constraints

- No xclim checkout
- A tiny directory layout with rootdir-subdir vs parent collection is the world

## Open Questions

- Can the tool list which conftest objects apply to each collected item without pytest internals dumps?

## Human Pressure

- There is no xclim tree. Continue using a two-directory fixture: conftest in a subdirectory rootdir, items collected from a parent path. Show which config applied to which item.

## Harvest Candidates

- Ask which configuration objects apply to items collected outside the rootdir

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: for each collected item, show which conftest/config objects actually apply
Nearest existing operation: pytest --collect-only plus reading conftest files
Observable delta: one query that shows a visibility hole when collection path is not a descendant of rootdir
Reason: collect-only lists items but not which conftest identity they bound
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no xclim tree. Continue using a two-directory fixture: conftest in subdir rootdir, tests collected from parent. Show which config applied to which item.

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
