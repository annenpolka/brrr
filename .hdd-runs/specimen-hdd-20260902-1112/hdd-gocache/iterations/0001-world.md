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
