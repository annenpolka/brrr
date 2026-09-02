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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
