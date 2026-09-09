def test_it(request):
    assert request.config.getoption("--db-url") == "scheme://host/db"
