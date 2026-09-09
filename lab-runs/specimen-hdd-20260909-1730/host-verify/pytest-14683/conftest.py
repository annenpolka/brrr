import pytest

@pytest.fixture(scope="session", autouse=True)
def doctest_setup(doctest_namespace):
    doctest_namespace["ANSWER"] = 42
