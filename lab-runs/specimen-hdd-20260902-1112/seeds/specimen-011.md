CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A tiny build cache keys freshness by *input hash only*. First build writes `out.bin`. Second build asks for an extra output `out.sbom` from the same inputs. Cache reports FRESH. `out.sbom` does not exist.

The developer wants to know what identity the cache used and which requested outputs were outside that identity.

# OBSERVED

Owned fixture files/cache_build.py. First build without extra output; second with extra output requested; FRESH; extra file missing.
first BUILT extra_exists False key 9280cc7e16e9
second FRESH extra_exists False key 9280cc7e16e9
same_key True

# COMMANDS

```
python3 files/cache_build.py
```

files/cache_build.py

RELEVANT MATERIAL

### cache_build.py

import hashlib, json, os, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    extra_path = outdir / "out.sbom"
    if extra and not extra_path.exists():
        # cache identity ignored extra; file missing on hit
        pass
    return status, extra_path.exists(), k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_exists", e1, "key", k1)
        print("second", s2, "extra_exists", e2, "key", k2)
        print("same_key", k1 == k2)

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
