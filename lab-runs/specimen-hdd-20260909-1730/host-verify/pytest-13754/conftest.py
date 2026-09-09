import pytest

def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "one_or_two" in metafunc.fixturenames:
        metafunc.parametrize("one_or_two", [1, 2], indirect=True)

@pytest.fixture(scope="module")
def one_or_two(request: pytest.FixtureRequest):
    print(request.param)

@pytest.fixture(scope="module")
def foo(one_or_two):
    print("foo")
