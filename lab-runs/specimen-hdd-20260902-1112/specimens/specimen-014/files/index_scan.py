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
