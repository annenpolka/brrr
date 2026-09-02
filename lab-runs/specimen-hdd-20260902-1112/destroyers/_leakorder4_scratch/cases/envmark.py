import os

def test_a():
    os.environ["LEAKORDER4_MARK"] = "1"

def test_b():
    assert "LEAKORDER4_MARK" not in os.environ
