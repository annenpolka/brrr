class Box:
    def __init__(self):
        self.bucket = []

box = Box()

def test_a():
    box.bucket.append("a")

def test_b():
    assert box.bucket == [], box.bucket
