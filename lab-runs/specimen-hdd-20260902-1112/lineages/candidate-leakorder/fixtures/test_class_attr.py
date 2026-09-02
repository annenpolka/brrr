class Box:
    bucket = []


def test_a():
    Box.bucket.append("a")


def test_b():
    assert Box.bucket == [], Box.bucket
