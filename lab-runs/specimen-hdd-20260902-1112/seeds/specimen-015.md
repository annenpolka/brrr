CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A display helper re-runs expressions to print “what happened”. A counter increments in the helper even when the original evaluation already ran. The developer wants to know which numbers came from the live evaluation versus the display path.

# OBSERVED

Owned fixture files/replay.py. `eval_count` is 1 after the real call and 2 after formatting the failure.
after_eval 1 calls 1
after_explain assert 2 calls 2

# COMMANDS

```
python3 files/replay.py
```

files/replay.py

RELEVANT MATERIAL

### replay.py

calls = {"n": 0}

def side():
    calls["n"] += 1
    return calls["n"]

val = side()
print("after_eval", val, "calls", calls["n"])

def explain(expr):
    # adversarial display path re-executes
    shown = expr()
    return f"assert {shown!r}"

msg = explain(side)
print("after_explain", msg, "calls", calls["n"])

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
