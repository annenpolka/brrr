import sys
acc = []

def test_a():
    sys.stdout.buffer.write(b"\xff\xfe")
    acc.append("a")

def test_b():
    assert acc == [], acc
