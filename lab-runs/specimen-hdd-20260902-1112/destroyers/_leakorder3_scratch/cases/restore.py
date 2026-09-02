acc = []

def test_a():
    acc.append("a")

def test_b():
    try:
        assert acc == [], acc
    finally:
        acc.clear()
