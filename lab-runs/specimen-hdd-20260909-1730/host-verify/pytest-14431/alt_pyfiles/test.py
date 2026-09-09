def add(a, b):
    return a + b

def test_add_multiple():
    assert add(1, 3) == 4
    assert add(1, 4) == 5
    assert add(2, 2) == 4
    assert add(0.1, 3.9) == 4
    assert add(1, 5) != 4
    assert add(1, 0.000000021) <= 4
    assert add(1, 100000000000000000000000.11) >= 4
    assert add(2, 2) == 4
    assert add(0, 0) == 0
    assert add(-1, 1) == 0
    assert add(100, 200) == 300
