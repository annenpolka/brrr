def test_capture_mode(pytestconfig):
    assert pytestconfig.option.capture == "sys"
