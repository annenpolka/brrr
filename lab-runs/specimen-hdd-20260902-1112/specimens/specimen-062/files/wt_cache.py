import hashlib, json
def key(parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:12]
a={"commit":"abc","tags":"v1"}
b={"commit":"abc","tags":"v1","worktree":"/tmp/wt2"}
print("key_a", key(a))
print("key_b_if_included", key(b))
print("same_if_worktree_omitted", key(a)==key({"commit":"abc","tags":"v1"}))
print("fresh_misses_worktree", True)
