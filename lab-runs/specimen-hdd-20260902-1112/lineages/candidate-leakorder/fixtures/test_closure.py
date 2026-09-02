def _wrap():
    acc = []

    def test_a():
        acc.append("a")

    def test_b():
        assert acc == [], acc

    return test_a, test_b


test_a, test_b = _wrap()
