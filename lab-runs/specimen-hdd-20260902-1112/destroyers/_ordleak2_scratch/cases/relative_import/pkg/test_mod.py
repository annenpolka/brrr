from .helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
