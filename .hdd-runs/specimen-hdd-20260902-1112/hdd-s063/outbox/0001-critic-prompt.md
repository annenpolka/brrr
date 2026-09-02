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

pytest-xdist with `--dist=loadgroup` hangs after a worker is replaced. Other distribution modes finish.

A two-test file, one worker, faulthandler killing the worker mid-run:

```
pytest -n1 --dist=loadgroup -o faulthandler_timeout=1 -o faulthandler_exit_on_timeout=true testing/test_timeout.py
```

Observed log, then stall:

```
replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
```

The developer wants to know which work units were put back on the queue after the crash, which of those units were already completed, and why the replacement worker never finishes.

# OBSERVED

Public pytest-dev/pytest-xdist#1323 / PR 1324. LoadScopeScheduling (`src/xdist/scheduler/loadscope.py`) is shared by `--dist=loadscope` and `--dist=loadgroup`.

Reporter file:

```
def test_1():
    assert True

def test_2():
    import time
    time.sleep(5)
    assert True
```

On the failing revision, `remove_node` after a crash does:

```
# Made uncompleted work unit available again
self.workqueue.update(workload)
```

`workload` is the crashed node's entire assigned dict: scope → {nodeid: completed_bool}. `update` puts *every* scope back, including scopes whose tests are already True.

Later `_assign_work_unit` pops a scope and builds:

```
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)
```

If the requeued unit has only completed items, `nodeids_indexes` is empty. `send_runtest_some([])` leaves the replacement worker waiting. Remote side hangs in `xdist/remote.py` around the runtest-some receive.

A PR acceptance case uses `os._exit(1)` in `test_b` after `test_a` passed, `-n1 --dist=loadgroup`. On the failing revision that suite never finishes.

This packet does not include a local clone; treat the snippets and hang as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
pytest -n1 --dist=loadgroup testing/test_timeout.py
# PR acceptance name:
#   test_loadgroup_does_not_hang_after_restart
```

Not executed on this lab host.

pytest-dev/pytest-xdist
  src/xdist/scheduler/loadscope.py
  src/xdist/remote.py
  testing/acceptance_test.py

RELEVANT MATERIAL

### hang_log.txt

replacing crashed worker gw0
collecting: 1/2 workers
collecting: 1/2 workers
2 workers [2 items]
# suite never finishes under --dist=loadgroup

### remove_node_failing.py

# Reduced excerpt of LoadScopeScheduling on failing_ref
# src/xdist/scheduler/loadscope.py

# inside remove_node, after identifying crashitem:
# Made uncompleted work unit available again
self.workqueue.update(workload)

# inside _assign_work_unit:
nodeids_indexes = [
    worker_collection.index(nodeid)
    for nodeid, completed in work_unit.items()
    if not completed
]
node.send_runtest_some(nodeids_indexes)

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

        Based on the provided material and observed behavior, I'll investigate the hang using the existing toolchain. The core issue occurs when a worker crashes in `--dist=loadgroup` mode and the replacement worker receives an empty test list. Here's the step-by-step investigation:

**1. Inspect worker status after crash replacement**  
```bash
pytest -n1 --dist=loadgroup testing/test_timeout.py \
  --debug | grep -E '(gw|crashed|replacing)'
```
*Output:*  
```
DEBUG    xdist.remote:remote.py:368] (1) <WorkerController gw0>:
DEBUG    xdist.workermanage:workermanage.py:496] Worker gw0 crashed: 
replacing crashed worker gw0
DEBUG    xdist.workermanage:workermanage.py:511] New worker 'gw1' started
```

**2. Capture scheduler queue state**  
```bash
pytest -n1 --dist=loadgroup testing/test_timeout.py \
  -o faulthandler_timeout=1 \
  --debug > scheduler_debug.log
```
*Relevant snippet from scheduler_debug.log:*  
```python
# After worker crash
DEBUG xdist.scheduler:loadscope.py:87] Workqueue pre-update: []
DEBUG xdist.scheduler:loadscope.py:89] Requeeing workload: 
  {'testing/test_timeout.py': {'test_1': True, 'test_2': False}}
DEBUG xdist.scheduler:loadscope.py:96] Workqueue post-update: 
  ['testing/test_timeout.py']
```

**3. Verify work unit processing for replacement worker**  
```bash
cat scheduler_debug.log | grep -A10 '_assign_work_unit'
```
*Output:*  
```python
DEBUG xdist.scheduler:loadscope.py:105] Assigning to gw1: scope=testing/test_timeout.py
DEBUG xdist.scheduler:loadscope.py:112] Work unit contents: 
  {'test_1': True, 'test_2': False}
DEBUG xdist.scheduler:loadscope.py:115] Nodeids indexes: [1]  # Correct non-empty list
```

**4. Trigger the hang scenario**  
Modify test to simulate completed work unit:  
```python
# test_timeout.py
def test_1(): pass
def test_2(): 
    import os; os._exit(1)  # Crash after test_1 completes
```
```bash
pytest -n1 --dist=loadgroup testing/test_timeout.py \
  --debug | grep -E '(send_runtest_some|indexes)'
```
*Output:*  
```python
DEBUG xdist.scheduler:loadscope.py:112] Work unit contents: 
  {'test_1': True, 'test_2': True}  # Unexpected completed state
DEBUG xdist.scheduler:loadscope.py:115] Nodeids indexes: []  # EMPTY
DEBUG xdist.scheduler:loadscope.py:117] Sending runtest_some: gw1 indices=()
```

**5. Confirm worker hang state**  
```bash
pytest -n1 --dist=loadgroup testing/test_timeout.py \
  --debug | grep -A5 'runtest_some'
```
*Output:*  
```python
DEBUG    xdist.remote:remote.py:375] (1) runtest_some: indices=()
# NO FURTHER OUTPUT - WORKER BLOCKED
```

**Root Cause Analysis**:  
The conflict arises from an unstated assumption in `remove_node()`: it assumes crash events only occur during *incomplete* tests. In reality, when a worker crashes immediately after completing all tests in its work unit (but before reporting back), the work unit is requeued with all tests marked completed. This causes:
1. The replacement worker receives an empty test list via `send_runtest_some([])`  
2. Worker enters indefinite wait in [`remote.py`'s execution loop](https://github.com/pytest-dev/pytest-xdist/blob/main/src/xdist/remote.py#L373)  
3. Scheduler waits for worker status that never arrives

**Resolution Path**:  
Modify work unit requeue logic to filter completed tests:  
```python
# In loadscope.py remove_node()
if workload:
    # Filter to only incomplete tests
    for scope, work_unit in workload.items():
        incomplete = {n: c for n, c in work_unit.items() if not c}
        if incomplete:
            self.workqueue.push(incomplete, scope)
```

This matches the observed failure mode while preserving the scheduler's core behavior for incomplete work units. The hanging worker scenario disappears because empty work units are never requeued.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
