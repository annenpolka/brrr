# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Paired runs of the same two tests. Besides the leaked `acc` list from specimen-009,
test_a also sets an extra module global `flag = True`. test_b asserts `acc == []`
and `flag is False`. Pair A (`test_b` then `test_a`) PASS. Pair B (`test_a` then
`test_b`) FAIL. Same files. Only order changes.

The developer wants one question that names both leaked objects without reading
both traces by hand.

# OBSERVED

Owned fixture files/run_orders_extra.py. Host-executed:

order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a'] flag_after True

order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a'] flag_after True

# COMMANDS

python3 files/run_orders_extra.py

TREE

files/run_orders_extra.py

RELEVANT MATERIAL

### run_orders_extra.py

#!/usr/bin/env python3
"""Owned order-contrast runner with an extra module global (no pytest)."""
from __future__ import annotations

def run(order):
    acc = []
    flag = False
    results = []

    def test_a():
        nonlocal flag
        acc.append("a")
        flag = True

    def test_b():
        assert acc == [], acc
        assert flag is False, flag

    fns = {"test_a": test_a, "test_b": test_b}
    for name in order:
        try:
            fns[name]()
            results.append((name, "PASS", None))
        except AssertionError as exc:
            results.append((name, "FAIL", str(exc)))
    return {"order": order, "results": results, "acc": list(acc), "flag": flag}

def main():
    for order in (("test_b", "test_a"), ("test_a", "test_b")):
        rec = run(order)
        print("order", rec["order"])
        for name, status, detail in rec["results"]:
            extra = f" {detail}" if detail else ""
            print(f"  {name} {status}{extra}")
        print("  acc_after", rec["acc"], "flag_after", rec["flag"])

if __name__ == "__main__":
    main()

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
