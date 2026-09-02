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
