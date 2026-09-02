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
