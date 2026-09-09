import pytest

DEFAULT = ["a", "b", "c"]

@pytest.fixture(params=DEFAULT)
def target(request):
    return request.param

@pytest.mark.parametrize(
    "target",
    ["a", "b"],
    indirect=True,
)
def test_foo(target):
    assert True
