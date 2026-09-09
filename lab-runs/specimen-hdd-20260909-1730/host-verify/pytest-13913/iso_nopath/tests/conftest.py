def pytest_addoption(parser):
    parser.addoption("--db", action="store", default=None)
    parser.addoption("--write-idents", action="store", default=None)
