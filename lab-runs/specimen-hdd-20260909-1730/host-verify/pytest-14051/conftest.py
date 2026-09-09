def pytest_addoption(parser):
    parser.addoption("--custom-arg", action="store", default=None)
