import pytest

@pytest.fixture(autouse=True)
def inner_fixture():
    print("inner_fixture")
