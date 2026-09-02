class Box:
    bucket = []

def test_a():
    Box.bucket.append("a")

def test_b():
    try:
        assert Box.bucket == [], Box.bucket
    finally:
        Box.bucket.clear()
