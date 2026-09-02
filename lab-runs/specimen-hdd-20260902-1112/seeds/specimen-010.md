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
