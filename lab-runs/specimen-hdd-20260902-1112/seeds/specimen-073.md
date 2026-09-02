CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK
A visitor inserts object addresses into a done-set. A later distinct value reuses an address after the first object is freed. The second node is skipped. The developer wants to know whether the visit set used pointer identity or value identity.

# OBSERVED
Owned files/visit_ptr.py.
first visit addr 4368654624
second visit addr 4368581648 values ['a', 'b']

python3 files/visit_ptr.py

files/visit_ptr.py

RELEVANT MATERIAL

### visit_ptr.py

class Node:
    def __init__(self, v):
        self.v = v

done_ptr = set()
seen_val = []

def visit_ptr(n):
    i = id(n)
    if i in done_ptr:
        return "skip-ptr"
    done_ptr.add(i)
    seen_val.append(n.v)
    return "visit"

a = Node("a")
print("first", visit_ptr(a), "addr", id(a))
del a
b = Node("b")
print("second", visit_ptr(b), "addr", id(b), "values", seen_val)

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
