import pytest
DEFAULT = ["a", "b", "c"]

@pytest.fixture(params=DEFAULT)
def target(request):
    return request.param
