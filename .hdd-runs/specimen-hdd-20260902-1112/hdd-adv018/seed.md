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
