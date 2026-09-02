import os
def test_a():
    pass
def test_b():
    raise AssertionError("pid=" + str(os.getpid()))
