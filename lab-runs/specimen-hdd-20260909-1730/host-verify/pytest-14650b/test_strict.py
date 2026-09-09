import pytest


def double(val):
    try:
        return 2 * int(val)
    except ValueError:
        return 2 * val


@pytest.mark.parametrize("val,expected", ((1, 2), ("1", 2)))
def test_double_accepts_str_and_int(val, expected):
    assert expected == double(val)
