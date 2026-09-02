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

You are in a working tree for a small Python service that prices parcel quotes.
The test suite and a direct call of the same function currently disagree.
Standard tools are present (python, pytest, git, rg). An unfamiliar developer CLI
is already installed in this environment. It is not a thin wrapper around a familiar
Unix tool. Discover it and use it on this problem. Operate what is present rather
than proposing a product. Show concrete commands, inputs, outputs, failures, retries,
and observations. Do not invent repository facts that contradict the material below.

WHAT IS ON DISK

```
quote-api/
  pyproject.toml
  quote/__init__.py
  quote/pricing.py
  quote/zones.py
  tests/test_quote.py
  .env
```

`quote/pricing.py` (as currently saved):

```python
from decimal import Decimal
from quote.zones import surcharge_for

BASE = Decimal("10.00")

def quote(origin: str, dest: str, *, kg: Decimal, declared: int) -> dict:
    extra = surcharge_for(origin, dest, kg=kg, declared=declared)
    total = BASE + extra["amount"]
    return {"total": total, "surcharges": [extra]}
```

`tests/test_quote.py`:

```python
from decimal import Decimal
from quote.pricing import quote

def test_zone_b_surcharge():
    q = quote("SEA", "PDX", kg=Decimal("2.4"), declared=40)
    assert q["total"] == Decimal("12.50")
    assert q["surcharges"] == [{"code": "ZONE_B", "amount": Decimal("2.50")}]
```

COMMANDS ALREADY RUN

```
$ git status -sb
## fix/zone-b
 M quote/pricing.py
 M quote/zones.py
 M tests/test_quote.py

$ pytest tests/test_quote.py -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
___________________________ test_zone_b_surcharge ____________________________
tests/test_quote.py:7: in test_zone_b_surcharge
    assert q["total"] == Decimal("12.50")
E   AssertionError: assert Decimal('15.00') == Decimal('12.50')
=========================== short test summary info ============================
FAILED tests/test_quote.py::test_zone_b_surcharge - AssertionError: assert Decimal('15.00') == Decimal('12.50')
1 failed in 0.08s

$ python -c 'from decimal import Decimal; from quote.pricing import quote; print(quote("SEA","PDX", kg=Decimal("2.4"), declared=40))'
{'total': Decimal('12.50'), 'surcharges': [{'code': 'ZONE_B', 'amount': Decimal('2.50')}]}

$ python -c 'import quote.pricing, quote.zones; print(quote.pricing.__file__); print(quote.zones.__file__)'
/Users/dev/quote-api/quote/pricing.py
/Users/dev/quote-api/quote/zones.py
```

KNOWN FACTS

Only the observations above are established. Do not assume a root cause.

OPERATOR REQUEST

An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Discover it and use it on the problem above.
Operate what is present rather than proposing a product.
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

        ### Field Report: Investigating Discrepancy with Unfamiliar CLI Tool  

**Observation Context**:  
- Test fails in pytest (returns `15.00`) but succeeds in direct Python call (returns `12.50`).  
- Files (`pricing.py`, `zones.py`) are confirmed identical in both runs.  
- Unfamiliar CLI tool is present; named `dv` (discovered via `which dv` → `/usr/local/bin/dv`).  

---

#### Step 1: Discovery of CLI Tool (`dv`)  
Ran `dv --help` to understand capabilities:  
```bash
$ dv --help
Developer Velocity Toolkit (v1.8)
Usage: dv <command> [args]

Commands:
  run      : Execute code/scripts with environment isolation
  envdiff  : Compare runtime environments between executions
  trace    : Trace function calls/module loads
  inspect  : Probe live module state
  watch    : Monitor file changes during execution
```  
**Observation**:  
- Tool focuses on environment isolation, tracing, and runtime inspection.  

---

#### Step 2: Isolate Test Execution with `dv run`  
Ran test via `dv` to detect environment leaks:  
```bash
$ dv run pytest tests/test_quote.py -q --tb=short
F                                                                 [100%]
================================= FAILURES =================================
___________________________ test_zone_b_surcharge __________________________
tests/test_quote.py:7: AssertionError: assert Decimal('15.00') == Decimal('12.50')
```  
**Observation**:  
- Failure persists. No change from baseline.  

---

#### Step 3: Trace Function Calls with `dv trace`  
Traced `surcharge_for` during test execution:  
```bash
$ dv trace --function surcharge_for pytest tests/test_quote.py -q
Tracing function: surcharge_for
[TRACE] quote.zones.surcharge_for('SEA', 'PDX', kg=Decimal('2.4'), declared=40) → {'code': 'ZONE_B', 'amount': Decimal('5.00')}
F                                                                 [100%]
```  
**Critical Observation**:  
- `surcharge_for` returns `5.00` during test (total: `10.00 + 5.00 = 15.00`) but returns `2.50` in direct call.  
- Conflict: Same function call yields `5.00` in pytest but `2.50` in direct execution.  

---

#### Step 4: Inspect Module State with `dv inspect`  
Compared `quote.zones` state during test vs. direct call:  
```bash
$ dv inspect quote.zones --during "dv run pytest -q"
Loaded module: quote.zones
Attributes:
  - BASE_SURCHARGE: Decimal('5.00')
  - ZONE_MAP: {...}
  - surcharge_for: <function>
  - test_mode: True  # Unexpected flag

$ dv inspect quote.zones --during "python -c 'import quote.pricing; print()'"
Loaded module: quote.zones
Attributes:
  - BASE_SURCHARGE: Decimal('2.50')
  - test_mode: False
```  
**Key Finding**:  
- Global `test_mode: True` only in pytest environment.  
- `BASE_SURCHARGE` is `5.00` when `test_mode=True`.  

---

#### Step 5: Trace Origin of `test_mode`  
Traced writes to `test_mode` in `quote.zones`:  
```bash
$ dv trace --write test_mode pytest tests/test_quote.py -q
[TRACE WRITE] quote.zones.test_mode = True (set by tests/conftest.py:42)
```  
**Discovery**:  
- `tests/conftest.py` (not previously listed) sets `test_mode=True` via pytest fixture.  
- File confirmed via `rg "conftest" -l` → `tests/conftest.py`.  

---

#### Step 6: Verify `conftest.py` Impact  
Temporarily disabled `conftest.py` and retested:  
```bash
$ mv tests/conftest.py tests/_conftest.py
$ dv run pytest tests/test_quote.py -q
.                                                                 [100%]
1 passed
```  
**Result**:  
- Test passes when `conftest.py` is disabled.  

---

### Conclusion  
**Root Cause**:  
- Pytest loads `tests/conftest.py`, which sets `quote.zones.test_mode = True`.  
- This overrides `BASE_SURCHARGE` to `5.00` during tests.  
- Direct call does not load `conftest.py`, hence uses `BASE_SURCHARGE=2.50`.  

**Resolver**:  
- The `conftest.py` fixture (auto-applied to all tests) is incompatible with this test.  
- Options:  
  1. Modify `conftest.py` to exclude `quote.zones` from test-mode overrides.  
  2. Refactor test to explicitly set `test_mode=False`.  

**Tool Utility**:  
- `dv` validated environment isolation discrepancies (`envdiff`).  
- `trace` and `inspect` exposed hidden state mutations.  
- Critical for diagnosing pytest vs. runtime context splits.  

**Next Action**:  
- Audit `tests/conftest.py` to scope test-mode overrides.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
