def pytest_addoption(parser):
    parser.addoption("--from-b", action="store_true", default=False)
