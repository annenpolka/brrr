import os


def test_a():
    os.environ["ORDLEAK_MARK"] = "a"


def test_b():
    assert "ORDLEAK_MARK" not in os.environ, os.environ.get("ORDLEAK_MARK")
