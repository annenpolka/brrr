import sys

def test_a():
    sys.modules["leakorder4_mod"] = object()

def test_b():
    assert "leakorder4_mod" not in sys.modules
