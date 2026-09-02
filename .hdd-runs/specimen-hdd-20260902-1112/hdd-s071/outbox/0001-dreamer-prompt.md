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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
