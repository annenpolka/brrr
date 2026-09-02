import sys


def test_a():
    sys.stdout.buffer.write(b"\xff\xfe")
    sys.stdout.buffer.flush()


def test_b():
    assert True
