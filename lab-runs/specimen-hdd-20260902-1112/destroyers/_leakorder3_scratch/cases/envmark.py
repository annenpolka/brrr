import os

def test_a():
    os.environ["LEAKORDER3_MARK"] = "1"

def test_b():
    assert "LEAKORDER3_MARK" not in os.environ
