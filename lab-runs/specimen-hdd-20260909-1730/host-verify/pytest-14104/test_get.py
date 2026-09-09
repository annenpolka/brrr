import pytest

@pytest.fixture(scope="session")
def foo(request):
    return getattr(request, "param", None)

@pytest.mark.parametrize("foo", [1], indirect=True)
def test_a(foo):
    assert foo == 1

def test_b(request):
    request.getfixturevalue("foo")

@pytest.mark.parametrize("foo", [1], indirect=True)
def test_c(foo):
    assert foo == 1
