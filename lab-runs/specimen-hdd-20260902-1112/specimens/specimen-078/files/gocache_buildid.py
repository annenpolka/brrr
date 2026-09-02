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
