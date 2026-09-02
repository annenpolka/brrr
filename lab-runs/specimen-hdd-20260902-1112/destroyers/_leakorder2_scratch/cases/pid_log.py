import os, sys
print(f"LOAD_PID {os.getpid()}", file=sys.stderr)
acc = []
def test_a():
    acc.append("a")
def test_b():
    assert acc == [], acc
