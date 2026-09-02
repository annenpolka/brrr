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

A cache record is printed as JSON. The record contains a hex `key`, an `inputs` object, and an `outputs` list that includes `out.sbom`. A second build requests `out.sbom` and prints FRESH. `out.sbom` does not exist.

The developer wants to know whether those listed output names participated in freshness, or only sat next to the identity in the dump.

# OBSERVED

Owned fixture files/cache_dump.py. The printed record lists `out.sbom` under `outputs`. The extra file is still missing on the second call. Keys match.

## Captured host execution (stdlib, no third-party packages)
```
record {"inputs": {"src": "hello"}, "key": "9280cc7e16e9", "outputs": ["out.bin", "out.sbom"]}
second FRESH extra_exists False key 9280cc7e16e9
outputs_listed_in_record True
same_key True
```

# COMMANDS

```
python3 files/cache_dump.py
```

files/cache_dump.py

RELEVANT MATERIAL

### cache_dump.py


#!/usr/bin/env python3
import hashlib
import json
import tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def main() -> None:
    cache = set()
    inputs = {"src": "hello"}
    outputs = ["out.bin", "out.sbom"]
    with tempfile.TemporaryDirectory() as td:
        outdir = Path(td)
        k = key(inputs)
        (outdir / "out.bin").write_text("bin")
        cache.add(k)
        record = {"key": k, "outputs": outputs, "inputs": inputs}
        print("record", json.dumps(record, sort_keys=True))
        k2 = key(inputs)
        extra = outdir / "out.sbom"
        print("second", "FRESH" if k2 in cache else "BUILT", "extra_exists", extra.exists(), "key", k2)
        print("outputs_listed_in_record", "out.sbom" in record["outputs"])
        print("same_key", k == k2)

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
