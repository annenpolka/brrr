import pytest
DEFAULT = ["a", "b", "c"]

@pytest.fixture(params=DEFAULT)
def target(request):
    return request.param

@pytest.mark.parametrize("target", ["a", "b"], indirect=True, ids=["A", "B"])
def test_foo(target):
    assert True
