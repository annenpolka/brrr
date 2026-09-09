def pytest_configure(config):
    print("GETINI_LOG_FORMAT", repr(config.getini("log_format")))
    print("GETINI_LOG_CLI", repr(config.getini("log_cli")))
