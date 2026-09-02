import helper

def test_a():
    helper.Box.bucket.append("a")

def test_b():
    assert helper.Box.bucket == [], helper.Box.bucket
