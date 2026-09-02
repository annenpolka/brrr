acc = []

def test_a():
    global acc
    acc.append("a")
    del acc

def test_b():
    assert "acc" not in globals() or acc == []
