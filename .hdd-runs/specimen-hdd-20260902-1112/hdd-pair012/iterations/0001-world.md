# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Paired runs of the same two tests. The only observed difference is test order. A: PASS. B: FAIL. The developer wants one question that names that difference without reading both traces by hand.

# OBSERVED

Pair A: `pytest test_b test_a` → PASS
Pair B: `pytest test_a test_b` → FAIL test_b assertion acc == []
Same files. Same interpreter. Only order changes.

# COMMANDS

Use files from specimen-009. A vs B as above.

files/test_order.py (same as specimen-009)

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
