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
