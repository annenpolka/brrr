from test_class_leak import test_a, test_b, Box

def run(order):
    Box.bucket.clear()
    fns={"test_a":test_a,"test_b":test_b}
    for n in order:
        try:
            fns[n](); print(n,"PASS")
        except AssertionError as e:
            print(n,"FAIL",e)

print("A then B")
run(("test_a","test_b"))
print("B then A")
run(("test_b","test_a"))
