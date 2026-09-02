from pkg import helper

def test_a():
    helper.bucket.append("a")

def test_b():
    assert helper.bucket == [], helper.bucket
