acc = []

def test_a():
    print("hello from test")
    acc.append("a")

def test_b():
    print('{"order": "fake"}')
    assert acc == [], acc
