import pkg.helper

def test_a():
    pkg.helper.bucket.append("a")

def test_b():
    assert pkg.helper.bucket == [], pkg.helper.bucket
