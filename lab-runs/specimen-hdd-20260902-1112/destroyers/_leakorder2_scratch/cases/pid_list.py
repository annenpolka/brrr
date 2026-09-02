import os
seen = []
def test_a():
    seen.append(os.getpid())
def test_b():
    seen.append(os.getpid())
