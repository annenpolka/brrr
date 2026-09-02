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

Home Assistant pytest collection: a parent directory appears more than once in the argument list. Fixtures registered from conftest are “not found” for tests collected after unrelated paths. Order of CLI path arguments changes whether fixtures resolve.

The developer wants to know whether the same directory is still the same collection object, and which fixture definitions are bound to which object identities.

# OBSERVED

Public issue pytest-dev/pytest#14635 / PR 14645.

Symptom: fixture closure computation fails for tests collected after unrelated paths. Conftest fixtures were registered against a Directory node that is no longer the node later collection looks up.

A regression test name on the PR: `test_fixture_closure_order_independence_with_parametrize`.

`--keep-duplicates file.py file.py` is still expected to collect the file twice (that behavior is separate).

# COMMANDS

```
pytest path/a path/b path/a --collect-only
```
Order of overlapping directory arguments changes fixture resolution on the failing revision.

<repo>/conftest.py
<repo>/tests/...
CLI args include a parent directory more than once

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
