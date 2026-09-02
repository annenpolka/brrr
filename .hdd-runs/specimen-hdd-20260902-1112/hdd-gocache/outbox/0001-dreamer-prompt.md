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

A test cache keys freshness by the test file list only. First run builds with binary buildid `buildid-aaa`. The binary is rewritten with `buildid-bbb`. Second run reports FRESH because the cache key ignored buildid.

The developer wants to know whether the cache key included the binary buildid, and whether FRESH reused a stale binary.

# OBSERVED

Owned files/gocache_buildid.py. Host-executed:

first BUILT key 55e3acdd667f buildid buildid-aaa
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa
same_key True
key_includes_buildid False
stale_binary True

# COMMANDS

python3 files/gocache_buildid.py

TREE

files/gocache_buildid.py

RELEVANT MATERIAL

### gocache_buildid.py

#!/usr/bin/env python3
"""Owned analog: test cache keyed by test files, not binary buildid."""
import hashlib, json

def test_key(test_files):
    return hashlib.sha256(json.dumps(test_files, sort_keys=True).encode()).hexdigest()[:12]

def main():
    tests = ["foo_test.go"]
    k1 = test_key(tests)
    buildid1 = "buildid-aaa"
    buildid2 = "buildid-bbb"
    k2 = test_key(tests)
    print("first", "BUILT", "key", k1, "buildid", buildid1)
    print("second", "FRESH", "key", k2, "buildid", buildid2, "cached_buildid", buildid1)
    print("same_key", k1 == k2)
    print("key_includes_buildid", False)
    print("stale_binary", buildid1 != buildid2 and k1 == k2)

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
