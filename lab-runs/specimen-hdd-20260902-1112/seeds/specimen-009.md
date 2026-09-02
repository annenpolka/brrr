CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Two tests share a module-level list. One test appends. The other asserts the list is empty. Depending on collection/run order, the suite is green or red. The developer wants a first-class view of *what leaked between tests* and *which order is sufficient to expose it*.

# OBSERVED

See files/test_order.py. Captured on this lab host (owned fixture, not untrusted OSS):

```
python3 -m pytest files/test_order.py -q --tb=line
# default file order (test_a then test_b): FAIL test_b
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
# reverse: PASS
```

## Captured host execution
```
--- reverse ---
```

## Captured host execution (stdlib runner, no pytest)
```
order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a']
order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a']
```

# COMMANDS

```
python3 -m pytest files/test_order.py -q --tb=line
python3 -m pytest files/test_order.py::test_b files/test_order.py::test_a -q --tb=line
```

files/test_order.py

RELEVANT MATERIAL

### run_orders.py

#!/usr/bin/env python3
"""Owned order-contrast runner (no third-party pytest)."""
from __future__ import annotations


def run(order: tuple[str, ...]) -> dict:
    acc: list[str] = []
    results = []

    def test_a():
        acc.append("a")

    def test_b():
        assert acc == [], acc

    fns = {"test_a": test_a, "test_b": test_b}
    for name in order:
        try:
            fns[name]()
            results.append((name, "PASS", None))
        except AssertionError as exc:
            results.append((name, "FAIL", str(exc)))
    return {"order": order, "results": results, "acc": list(acc)}


def main() -> None:
    for order in (("test_a", "test_b"), ("test_b", "test_a")):
        rec = run(order)
        print("order", rec["order"])
        for name, status, detail in rec["results"]:
            extra = f" {detail}" if detail else ""
            print(f"  {name} {status}{extra}")
        print("  acc_after", rec["acc"])


if __name__ == "__main__":
    main()

### test_order.py

acc = []

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc

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
