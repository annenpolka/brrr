import builtins
orig = builtins.abs
def test_a():
    builtins.abs = lambda x: 0
def test_b():
    assert builtins.abs is orig
