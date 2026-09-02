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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
