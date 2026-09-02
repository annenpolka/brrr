# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A tiny build cache keys freshness by input hash only. First build writes `out.bin`
and also writes an empty `out.sbom` stub as a side effect of hashing (extra was
not requested). Second build asks for extra output `out.sbom` from the same
inputs. Cache reports FRESH. `out.sbom` exists. Its bytes are the empty stub.

The developer wants to know whether the extra file was produced for this request
or leftover from the identity write, and which requested outputs were outside
that identity.

# OBSERVED

Owned fixture files/cache_build_stub.py. Host-executed:

first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9
second FRESH extra_requested True extra_exists True extra_bytes 0 key 9280cc7e16e9
same_key True
stub_leftover True

# COMMANDS

python3 files/cache_build_stub.py

TREE

files/cache_build_stub.py

RELEVANT MATERIAL

### cache_build_stub.py

import hashlib, json, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    extra_path = outdir / "out.sbom"
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        extra_path.write_text("")
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    return status, extra_path.exists(), extra_path.stat().st_size, k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, n1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, n2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_requested", False, "extra_exists", e1, "extra_bytes", n1, "key", k1)
        print("second", s2, "extra_requested", True, "extra_exists", e2, "extra_bytes", n2, "key", k2)
        print("same_key", k1 == k2)
        print("stub_leftover", e2 and n2 == 0)

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
