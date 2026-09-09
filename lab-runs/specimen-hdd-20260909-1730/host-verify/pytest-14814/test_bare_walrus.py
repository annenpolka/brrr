def identity(value):
    return value

def collect(*values):
    return values

def test_bare_walrus_args():
    assert collect(x := 1, identity(x := 2)) == (1, 2)
