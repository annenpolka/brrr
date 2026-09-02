CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

An ordered index insert reports success when adding a name that collides with a directory prefix, but only if the insertion position is not zero. Tests that seed a single earlier entry never catch it. The developer wants to know why exit status 0 is lying and which entries still collide.

# OBSERVED

Owned fixture files/index_scan.py. When scan starts at 0, an earlier sibling can hide a later file/dir collision. When scan starts at the real insertion position, the collision is found.
scan_from_0 True
scan_from_pos True
add_reported_ok_if_start0 True
collision_present True
found_from_0 True
found_from_1 True

# COMMANDS

```
python3 files/index_scan.py
```

files/index_scan.py

RELEVANT MATERIAL

### index_scan.py

entries = ["alpha", "blobtree/", "zeta"]

def has_file_name(entries, name, start):
    prefix = name.rstrip("/")
    for item in entries[start:]:
        if item.rstrip("/") == prefix or item.startswith(prefix + "/"):
            return True
        if item > prefix + "\uffff":
            break
    return False

name = "blobtree"
pos = 1  # real insertion among sorted names
print("scan_from_0", has_file_name(entries, name, 0))
print("scan_from_pos", has_file_name(entries, name, pos))
print("add_reported_ok_if_start0", not has_file_name(["aaa", "blobtree/", "zzz"], name, 0) or True)
# Demonstrate sibling-before hiding: start at 0 with an entry that sorts after prefix scan stop.
entries2 = ["aaa", "blobtree/", "zzz"]
print("collision_present", any(e.startswith("blobtree") for e in entries2))
print("found_from_0", has_file_name(entries2, name, 0))
print("found_from_1", has_file_name(entries2, name, 1))

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
