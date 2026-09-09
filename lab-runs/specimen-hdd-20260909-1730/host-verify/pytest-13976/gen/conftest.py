import pytest
DEFAULT = ["a", "b", "c"]

@pytest.fixture
def target(request):
    return request.param

def pytest_generate_tests(metafunc):
    if "target" not in metafunc.fixturenames:
        return
    if any(m.name == "parametrize" and "target" in str(m.args) for m in metafunc.definition.iter_markers("parametrize")):
        return
    metafunc.parametrize("target", DEFAULT, indirect=True)
