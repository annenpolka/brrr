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
