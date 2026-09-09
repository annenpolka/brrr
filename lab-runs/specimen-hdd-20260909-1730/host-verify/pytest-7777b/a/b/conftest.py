import pytest
@pytest.fixture(scope="package")
def pkg_b():
    print("SETUP pkg_b")
    yield "b"
    print("TEARDOWN pkg_b")
