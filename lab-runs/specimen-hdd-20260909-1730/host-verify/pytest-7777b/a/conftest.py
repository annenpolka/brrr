import pytest
@pytest.fixture(scope="package")
def pkg_a():
    print("SETUP pkg_a")
    yield "a"
    print("TEARDOWN pkg_a")
