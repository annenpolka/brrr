def identity(value):
    return value

def collect(*values):
    return values

def test_walrus_tuple_arg():
    assert collect((x := 1), identity(x := 2)) == (1, 2)

def test_starred_arg():
    items = [1]
    assert collect(*items, identity(items := [9])) == (1, [9])
