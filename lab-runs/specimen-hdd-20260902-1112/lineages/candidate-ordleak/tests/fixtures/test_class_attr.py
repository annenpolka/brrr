class Box:
    items = []


def test_a():
    Box.items.append("a")


def test_b():
    assert Box.items == [], Box.items
