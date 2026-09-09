import pytest

@pytest.mark.parametrize("target", ["a", "b"], indirect=True)
def test_foo(target):
    assert True
