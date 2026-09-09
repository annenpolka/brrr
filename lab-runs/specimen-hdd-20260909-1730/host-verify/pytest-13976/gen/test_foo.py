import pytest

@pytest.mark.parametrize("target", ["a", "b"], indirect=True)
def test_foo(target):
    assert True

def test_default(target):
    assert target in ("a", "b", "c")
