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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
