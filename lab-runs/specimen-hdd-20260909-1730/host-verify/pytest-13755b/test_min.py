import pytest
seen = set()

@pytest.fixture(scope="session")
def fix_once(request):
    assert request.param not in seen, seen
    seen.add(request.param)

@pytest.fixture()
def fixture2(request):
    return request.param

@pytest.mark.parametrize("fix_once", ["a", "b"], indirect=True)
def test_a(fix_once):
    pass

@pytest.mark.parametrize("fix_once, fixture2", [("a", "x"), ("b", "x")], indirect=True)
def test_b(fix_once, fixture2):
    pass
