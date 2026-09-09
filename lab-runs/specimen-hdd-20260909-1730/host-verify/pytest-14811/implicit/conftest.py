def pytest_addoption(parser):
    parser.addini("mystr", "string option", default="x")
