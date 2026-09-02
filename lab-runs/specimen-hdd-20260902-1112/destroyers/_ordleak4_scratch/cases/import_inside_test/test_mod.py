def test_a():
    from helper import bucket
    bucket.append("a")

def test_b():
    from helper import bucket
    assert bucket == [], bucket
