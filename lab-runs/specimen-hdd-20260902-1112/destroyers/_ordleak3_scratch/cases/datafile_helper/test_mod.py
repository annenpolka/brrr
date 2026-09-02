import helper

def test_a():
    helper.bucket.append(helper.DATA)

def test_b():
    assert helper.bucket == [], helper.bucket
