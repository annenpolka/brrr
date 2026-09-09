import pytest
DEFAULT = ["a", "b", "c"]

@pytest.fixture(params=DEFAULT)
def target(request):
    return request.param

@pytest.mark.parametrize("target", [pytest.param("a"), pytest.param("b")], indirect=True)
def test_foo(target):
    assert True
