def test_subscript():
    assert {'a': 1, 'b': 2}['a'] == 99


def test_ifexp():
    assert (0 if True else 1) == 99
