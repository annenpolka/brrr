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

Process inherits `KEY=/x`. A dotenv-style file contains `KEY=`. After load, some tools still see `/x`, some see empty, some fall back to a default. The developer wants to know which layer treated empty as “unset” and which value actually won.

# OBSERVED

Owned fixture files/loader.py:

Inherited KEY=/x plus file `KEY=` (empty assignment).

Naive loader that skips falsey values leaves inherited `/x`.
A loader that always assigns stores empty string.

See COMMANDS for captured prints.
skip_empty '/x' '2'
assign '' '2'
unset_vs_empty False None

# COMMANDS

```
python3 files/loader.py
```

files/loader.py

RELEVANT MATERIAL

### loader.py

import os

inherited = {"KEY": "/x", "OTHER": "1"}
file_text = "KEY=\nOTHER=2\n"

def load_skip_empty(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        if v:
            out[k] = v
    return out

def load_assign(env_text, base):
    out = dict(base)
    for line in env_text.splitlines():
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k] = v
    return out

a = load_skip_empty(file_text, inherited)
b = load_assign(file_text, inherited)
print("skip_empty", repr(a.get("KEY")), repr(a.get("OTHER")))
print("assign", repr(b.get("KEY")), repr(b.get("OTHER")))
print("unset_vs_empty", "KEY" in os.environ, repr(os.environ.get("KEY")))

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
