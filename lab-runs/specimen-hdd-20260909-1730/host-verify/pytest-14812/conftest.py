import pytest


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if call.when == "teardown" and "caplog" in getattr(item, "funcargs", {}):
        caplog = item.funcargs["caplog"]
        _ = caplog.text
        _ = caplog.get_records("call")
    return report
