import pytest


@pytest.fixture
def sample():
    """Fixture with a doctest.

    >>> 1 + 1
    2
    """
    return 1


@pytest.fixture
def skipped_doc():
    """Skipped doctest on a fixture wrapper.

    >>> import pytest
    >>> pytest.skip("skip-in-doctest")
    """
    return 1


def test_uses_sample(sample):
    assert sample == 1
