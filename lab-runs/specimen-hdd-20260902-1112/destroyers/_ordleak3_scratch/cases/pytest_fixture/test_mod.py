def test_a(ready):
    ready.append("a")

def test_b(ready):
    assert ready == []
