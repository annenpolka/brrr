from __future__ import annotations

from collections.abc import Generator
import pytest


pytest_plugins = 'pytester'


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addini(
        'skip_by_default',
        'skip the tests marked with `@pytest.mark.skip_by_default`',
        type='bool',
        default=True,
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        'markers',
        'skip_by_default: '
        'skip the test by default, '
        'unless the eponymous ini option is set to false',
    )


@pytest.hookimpl(wrapper=True)
def pytest_collection_modifyitems(
    items: list[pytest.Item], config: pytest.Config,
) -> Generator[None, None, Exception | None]:
    """
    Drop the `@pytest.mark.skip_by_default` tests by default.
    """
    result: Exception | None = (yield)

    if not config.getini('skip_by_default'):
        return result

    n = len(items)
    for offset, item in enumerate(reversed(items), 1):
        if any(
            mark.name == 'skip_by_default' for mark in item.iter_markers()
        ):
            del items[n - offset]
    return result
