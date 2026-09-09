def test_b(request):
    assert request.config.getoption("--from-b") in (True, False)
