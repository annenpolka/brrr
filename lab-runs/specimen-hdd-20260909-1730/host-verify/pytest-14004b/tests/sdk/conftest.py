import pytest

@pytest.fixture(autouse=True)
def outer_fixture():
    print("outer_fixture")
