acc = []

def test_a():
    acc.append("a")

def test_b():
    global acc
    try:
        assert acc == [], acc
    finally:
        acc = []
