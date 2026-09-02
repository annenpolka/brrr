import sys
def test_a():
    sys.modules["leakorder2_secret"] = sys
def test_b():
    assert "leakorder2_secret" not in sys.modules
