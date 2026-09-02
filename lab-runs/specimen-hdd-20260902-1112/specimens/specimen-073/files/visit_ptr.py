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
