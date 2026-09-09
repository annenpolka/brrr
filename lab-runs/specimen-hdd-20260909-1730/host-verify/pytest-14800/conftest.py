import pytest

@pytest.hookimpl(tryfirst=True)
def pytest_fixture_setup(fixturedef, request):
    param = getattr(request, "param", None)
    if isinstance(param, str) and param.startswith("fixture:"):
        request.param = request.getfixturevalue(param[len("fixture:"):])
