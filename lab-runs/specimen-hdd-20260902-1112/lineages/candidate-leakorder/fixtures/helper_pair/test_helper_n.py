import helper


def test_a():
    helper.n += 1


def test_b():
    helper.n += 10
    raise AssertionError("n=" + str(helper.n))
