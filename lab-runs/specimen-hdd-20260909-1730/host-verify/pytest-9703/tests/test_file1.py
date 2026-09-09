import pytest

@pytest.fixture(autouse=True)
def some_fixture():
    print("Fixture called")

def test_in_file1():
    print("test_in_file1")
