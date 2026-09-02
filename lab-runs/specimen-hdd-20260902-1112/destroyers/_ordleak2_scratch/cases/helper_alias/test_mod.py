import helper as h

def test_a():
    h.bucket.append("a")

def test_b():
    assert h.bucket == [], h.bucket
