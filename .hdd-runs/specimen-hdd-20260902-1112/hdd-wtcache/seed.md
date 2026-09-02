CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK
A cache key is hashed from commit and tags. A linked worktree path changed. Second build is FRESH. Extra worktree-local file is missing. Which identity component was omitted from the key?

# OBSERVED
Owned files/wt_cache.py.

python3 files/wt_cache.py

files/wt_cache.py

RELEVANT MATERIAL

### expand_ranges_failing.py

# Reduced excerpt of expand_ranges on failing_ref
# src/tox/config/loader/ini/factor.py

return re.sub(
    r"""
    (                       # outer capture group
        ( \d+ ) - ( \d+ )   # closed range: start-end
        |
        ( \d+ ) -           # right-open range: start-
        |
        (?<= [{,] ) - ( \d+ )  # left-open range: -end (preceded by { or ,)
        |
        \d+                 # single number
    )
    (?: , | \} )            # followed by comma or closing brace
    """,
    _expand,
    value,
    flags=re.VERBOSE,
)

### observed_expansions.txt

written: py313-django4-2
produced: py313-django4 , 3 , 2
missing:  py313-django4-2

written: py310-1,py310-2
produced: hundreds of names counting down from 310

written: {2-4}
produced: {2,3,4}   (still wanted)

written: py3{10-11}
produced: py310, py311   (still wanted)

### wt_cache.py

import hashlib, json
def key(parts):
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:12]
a={"commit":"abc","tags":"v1"}
b={"commit":"abc","tags":"v1","worktree":"/tmp/wt2"}
print("key_a", key(a))
print("key_b_if_included", key(b))
print("same_if_worktree_omitted", key(a)==key({"commit":"abc","tags":"v1"}))
print("fresh_misses_worktree", True)

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
