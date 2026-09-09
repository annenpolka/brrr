import pytest


@pytest.fixture(autouse=True)
def add_answer(doctest_namespace):
    doctest_namespace["ANSWER"] = 42
