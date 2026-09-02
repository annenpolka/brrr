#!/usr/bin/env python3
"""Owned analog: unused property in a full snapshot invalidates identity."""
import hashlib, json

USED = ("path",)
UNUSED = "idea.io.use.nio2"

def ident(props, mode):
    if mode == "all":
        payload = json.dumps(props, sort_keys=True)
    else:
        payload = json.dumps({k: props[k] for k in USED if k in props}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]

def main():
    a = {"path": "/app", UNUSED: "false"}
    b = {"path": "/app", UNUSED: "true"}
    print("used_keys", *USED)
    print("unused", UNUSED)
    print("all_first", ident(a, "all"), "all_second", ident(b, "all"), "all_same", ident(a, "all") == ident(b, "all"))
    print("used_first", ident(a, "used"), "used_second", ident(b, "used"), "used_same", ident(a, "used") == ident(b, "used"))
    print("invalidate_unused", ident(a, "all") != ident(b, "all") and ident(a, "used") == ident(b, "used"))

if __name__ == "__main__":
    main()
