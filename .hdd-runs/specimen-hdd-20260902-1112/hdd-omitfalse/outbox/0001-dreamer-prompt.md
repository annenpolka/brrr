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

Two encodings of the same record `{flag: false, name: x}`. Encoder A omits `flag` because it is false. Encoder B includes `"flag": false`. Downstream treats missing key as true.

The developer wants to know which encoder dropped the false and whether the decoded object still has the key.

# OBSERVED

Owned files/two_encoders.py. Host-executed:

A {"name": "x"}
B {"flag": false, "name": "x"}
A_has_flag False
B_has_flag True

# COMMANDS

python3 files/two_encoders.py

TREE

files/two_encoders.py

RELEVANT MATERIAL

### two_encoders.py

import json

def enc_a(obj):
    return json.dumps({k: v for k, v in obj.items() if v is not False})

def enc_b(obj):
    return json.dumps(obj)

def main():
    rec = {"flag": False, "name": "x"}
    a = enc_a(rec)
    b = enc_b(rec)
    print("A", a)
    print("B", b)
    print("A_has_flag", "flag" in json.loads(a))
    print("B_has_flag", "flag" in json.loads(b))

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
