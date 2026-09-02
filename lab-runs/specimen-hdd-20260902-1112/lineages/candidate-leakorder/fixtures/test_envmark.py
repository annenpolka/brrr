import os


def test_a():
    os.environ["LEAKORDER_MARK"] = "1"


def test_b():
    assert "LEAKORDER_MARK" not in os.environ
