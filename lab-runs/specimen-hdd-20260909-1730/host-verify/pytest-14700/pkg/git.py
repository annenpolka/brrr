"""Module collected like jaraco.test.git (not a test_*.py name)."""

import pytest


@pytest.fixture
def ensure_checkout():
    """Skipped doctest on a fixture wrapper.

    >>> import pytest
    >>> pytest.skip("needs git")
    """
    return 1


def not_a_test():
    return 1
