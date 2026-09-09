def pytest_addoption(parser):
    parser.addini("mystr", "string option", type="string", default="x")
