import sys

def test_a():
    sys.modules["leakorder3_mod"] = object()

def test_b():
    assert "leakorder3_mod" not in sys.modules
