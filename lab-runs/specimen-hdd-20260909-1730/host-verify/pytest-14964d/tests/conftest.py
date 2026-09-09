import pytest
@pytest.fixture(autouse=True)
def guard():
    raise RuntimeError("guard ran")
