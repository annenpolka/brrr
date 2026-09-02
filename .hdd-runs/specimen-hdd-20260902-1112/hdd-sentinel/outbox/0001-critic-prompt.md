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

A PEP 661 sentinel is passed as `dict.get`'s default. mypy infers the result as `str | sentinel` (the shared class), not `str | Unknown` (the value).

```
from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
```

```
test.py:8: error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
```

A sibling case: `ALIAS = MISSING` then `assert_type(ALIAS, sentinel)` passes on the failing revision, and `func(ALIAS)` is rejected as type `Sentinel` rather than `MISSING`.

The developer wants to know which identity the checker kept after substituting the TypeVar in `dict.get`, and where the literal attached to `Unknown` went.

# OBSERVED

Public python/mypy#21866 / PR 21888. Failing world around `mypy/expandtype.py` `visit_type_var` and `test-data/unit/check-sentinels.test`.

`dict.get` is overloaded with a TypeVar default. Substituting `Unknown` (an `Instance` whose `last_known_value` is the sentinel literal) hits:

```
repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
```

After that copy, the type prints as the fallback class name `sentinel` / `Sentinel`, not `Unknown`.

In-tree `testSentinelReassignmentIsNotTypeAlias` on the failing revision:

```
MISSING = sentinel("MISSING")
ALIAS = MISSING
assert_type(ALIAS, sentinel)
func(ALIAS)  # E: Argument 1 to "func" has incompatible type "Sentinel"; expected "int | MISSING"
```

`reveal_type` on a bare sentinel value is supposed to show the value's name (e.g. `Unknown?`), while the class `sentinel` remains the type of the constructor.

This packet does not include a local clone; treat the snippets and error as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
mypy test.py
# in-tree:
pytest mypy/test/testcheck.py -k sentinels
```

Not executed on this lab host.

python/mypy
  mypy/expandtype.py
  mypy/erasetype.py
  mypy/messages.py
  test-data/unit/check-sentinels.test

RELEVANT MATERIAL

### dict_get_sentinel.py

from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
    # failing revision:
    # error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]

### visit_type_var_failing.py

# Reduced excerpt of TypeExpander.visit_type_var on failing_ref
# mypy/expandtype.py

repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
return repl

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

        ### Field Report: Investigating Sentinel Inference in mypy

**Command Sequence & Observations:**

1. **Inspecting the failing test case:**
```bash
cat test.py
```
```python
from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
```

2. **Running mypy on minimal reproducer:**
```bash
mypy test.py
```
```
test.py:8: error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
Found 1 error in 1 file (checked 1 source file)
```
**Observation:** Confirms sentinel identity is lost during `dict.get` type inference.

3. **Examining type expansion logic:**
```bash
grep -A 10 "visit_type_var" mypy/expandtype.py
```
```python
repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
return repl
```
**Observation:** The `last_known_value` reset erases sentinel identity during typevar substitution.

4. **Testing sentinel reassignment behavior:**
```bash
pytest mypy/test/testcheck.py -k testSentinelReassignmentIsNotTypeAlias
```
```python
# In-tree test snippet:
MISSING = sentinel("MISSING")
ALIAS = MISSING
assert_type(ALIAS, sentinel)  # Passes in failing revision
func(ALIAS)  # Fails: Expected "int | MISSING", got "Sentinel"
```
**Observation:** Sentinel aliases lose value identity but retain class typing.

5. **Probing sentinel representation:**
```bash
grep -r "last_known_value" mypy/
```
**Relevant findings:**
- `mypy/erasetype.py`: Handles literal erasure but not sentinels
- `mypy/messages.py`: Error formatting uses `type.str_with_options()` for display
- `test-data/unit/check-sentinels.test`: Contains sentinel test expectations

**Hypothesis Testing:**

**Attempt 1:** Preserve `last_known_value` for sentinels in typevar expansion
```diff
# Modified expandtype.py
if isinstance(repl, ProperType) and isinstance(repl, Instance):
+   if "Sentinel" in repl.type.name:
+       return repl  # Skip reset for sentinels
    return repl.copy_modified(last_known_value=None)
```
**Result:** (Simulated via code inspection)
- `testSentinelReassignmentIsNotTypeAlias` fails: `ALIAS` now types as `MISSING` not `sentinel`
- 6 other sentinel tests fail due to changed identity propagation
- Original `dict.get` test passes

**Attempt 2:** Modify sentinel display logic
```python
# In mypy/messages.py
def format_sentinel_type(t: Instance) -> str:
    if t.last_known_value and hasattr(t.last_known_value, 'name'):
        return t.last_known_value.name
    return t.type.name
```
**Result:** 
- Error messages now show `Unknown` instead of `sentinel`
- Does not fix underlying type equivalence in `assert_type`
- Causes 12 test failures where `reveal_type` outputs change

**Key Conflict:** 
The `last_known_value` reset exists to normalize primitive literals for `reveal_type` consistency. Sentinels require opposite behavior - preserving value identity during typevar substitution. No single location resolves both requirements.

**Operational Findings:**
1. The sentinel's identity (`Unknown`) is stored in `Instance.last_known_value`
2. Typevar substitution in `dict.get`'s overload triggers `last_known_value` reset
3. Two competing needs:
   - Literal normalization requires value erasure
   - Sentinel typing requires value preservation
4. Current type system lacks sentinel-specific expansion rules

**Recommended Next Steps:**
1. Add sentinel flag to `Instance` type
2. Modify `TypeExpander.visit_type_var`:
```python
if isinstance(repl, Instance) and not repl.is_sentinel:
    return repl.copy_modified(last_known_value=None)
```
3. Update sentinel construction in `typing_extensions` to set `is_sentinel=True`

**Unresolved Constraints:**
- Requires coordinated changes in mypy and typing_extensions
- 40+ tests depend on current literal erasure behavior
- Sentinel identity vs class typing conflict needs design decision

**Conclusion:** The typechecker's literal normalization heuristic conflicts with sentinel value preservation. Resolution requires type system changes to distinguish sentinels from primitive literals during type expansion.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
